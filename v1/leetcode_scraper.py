"""
LeetCode 网页抓取模块 - Playwright 版本（修复版）
职责：从 LeetCode 网页提取问题详细信息
使用 Playwright 解决反爬虫问题（HTTP 403）
遵循 CleanRL 设计原则：单一职责、显式依赖、易于测试

修复内容：
1. 修复订阅检测误报问题
2. 改进内容提取逻辑
3. 添加更多选择器支持
"""
import sys
import time
import random
import traceback
from typing import List, Optional, Callable
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page, TimeoutError as PlaywrightTimeout
from loguru import logger

from leetcode_models import LeetCodeProblem, SimilarQuestion, Difficulty


class LeetCodeScraperPlaywright:
    """
    LeetCode 网页抓取器 - 使用 Playwright
    
    负责：
    1. 使用 Playwright 模拟真实浏览器访问
    2. 从 LeetCode 页面提取问题详情
    3. 处理需要订阅的页面
    4. 错误处理和智能重试
    5. 反检测优化
    """
    
    def __init__(
        self,
        timeout: int = 30000,  # Playwright 使用毫秒
        max_retries: int = 3,
        min_delay: float = 2.0,
        max_delay: float = 5.0,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
        headless: bool = True,
        block_resources: bool = True,
    ):
        """
        初始化抓取器
        
        Args:
            timeout: 页面超时时间（毫秒）
            max_retries: 最大重试次数
            min_delay: 最小请求间隔（秒）
            max_delay: 最大请求间隔（秒）
            progress_callback: 进度回调函数
            headless: 是否使用无头模式
            block_resources: 是否阻止非必要资源（图片、字体等）
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.progress_callback = progress_callback
        self.headless = headless
        self.block_resources = block_resources
        
        # Playwright 实例
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        
    def __enter__(self):
        """上下文管理器入口"""
        self._start_browser()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self._close_browser()
    
    def _start_browser(self):
        """启动浏览器"""
        logger.info("启动 Playwright 浏览器...")
        
        self.playwright = sync_playwright().start()
        
        # 启动 Chromium（最好的反检测支持）
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--disable-blink-features=AutomationControlled',  # 隐藏自动化特征
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--disable-setuid-sandbox',
            ]
        )
        
        # 创建浏览器上下文，模拟真实浏览器
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            locale='en-US',
            timezone_id='America/New_York',
            permissions=['geolocation'],
            color_scheme='light',
            accept_downloads=False,
            ignore_https_errors=False,
            # 添加额外的浏览器特征
            extra_http_headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Cache-Control': 'max-age=0',
            }
        )
        
        # 注入 JavaScript 隐藏 webdriver 特征
        self.context.add_init_script("""
            // 隐藏 webdriver 属性
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            
            // 添加 Chrome 特征
            window.chrome = {
                runtime: {}
            };
            
            // 隐藏 Playwright 特征
            delete window.__playwright;
            delete window.__pw_manual;
            delete window.__PW_inspect;
        """)
        
        logger.info("浏览器启动成功")
    
    def _close_browser(self):
        """关闭浏览器"""
        logger.info("关闭浏览器...")
        
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def _report_progress(self, message: str, current: int, total: int):
        """报告进度"""
        if self.progress_callback:
            self.progress_callback(message, current, total)
        else:
            percentage = (current / total * 100) if total > 0 else 0
            logger.info(f"[{percentage:.1f}%] {message}")
    
    def _random_delay(self):
        """随机延迟，模拟人类行为"""
        delay = random.uniform(self.min_delay, self.max_delay)
        logger.debug(f"等待 {delay:.2f} 秒...")
        time.sleep(delay)
    
    def _setup_resource_blocking(self, page: Page):
        """设置资源阻止，提升性能"""
        if not self.block_resources:
            return
        
        def block_resources(route, request):
            """阻止不必要的资源"""
            resource_type = request.resource_type
            if resource_type in ['image', 'media', 'font', 'stylesheet']:
                route.abort()
            else:
                route.continue_()
        
        page.route("**/*", block_resources)
    
    def _simulate_human_behavior(self, page: Page):
        """模拟人类浏览行为"""
        try:
            # 随机滚动
            scroll_height = page.evaluate("document.body.scrollHeight")
            scroll_to = random.randint(100, min(500, scroll_height // 2))
            page.evaluate(f"window.scrollTo(0, {scroll_to})")
            time.sleep(random.uniform(0.5, 1.5))
            
            # 滚动回顶部
            page.evaluate("window.scrollTo(0, 0)")
            time.sleep(random.uniform(0.3, 0.8))
        except Exception as e:
            logger.debug(f"模拟行为失败: {e}")
    
    def scrape_problem(self, problem: LeetCodeProblem) -> bool:
        """
        抓取单个问题的详细信息
        
        Args:
            problem: LeetCode 问题对象（将被修改）
            
        Returns:
            是否成功抓取
        """
        logger.info(f"抓取问题: {problem.display_title}")
        
        for attempt in range(self.max_retries):
            page = None
            try:
                # 速率限制
                if attempt > 0:
                    # 指数退避
                    delay = self.min_delay * (2 ** attempt) + random.uniform(0, 2)
                    logger.info(f"重试 {attempt + 1}/{self.max_retries}，等待 {delay:.2f} 秒")
                    time.sleep(delay)
                else:
                    self._random_delay()
                
                # 创建新页面
                page = self.context.new_page()
                
                # 设置资源阻止
                self._setup_resource_blocking(page)
                
                # 访问页面
                logger.debug(f"访问 URL: {problem.href}")
                response = page.goto(
                    problem.href,
                    wait_until='domcontentloaded',
                    timeout=self.timeout
                )
                
                # 检查响应状态
                if response and response.status == 403:
                    logger.warning(f"HTTP 403 for {problem.href}")
                    page.close()
                    continue
                
                if response and response.status != 200:
                    logger.warning(f"HTTP {response.status} for {problem.href}")
                    page.close()
                    continue
                
                # 等待页面加载
                try:
                    # 等待主要内容加载（可能需要根据实际页面结构调整选择器）
                    page.wait_for_selector('[class*="description"]', timeout=10000)
                except PlaywrightTimeout:
                    logger.debug("等待描述超时，继续处理...")
                
                # 模拟人类行为
                self._simulate_human_behavior(page)
                
                # 检查是否需要订阅（修复：直接传入 page 对象）
                if self._check_subscription_required(page):
                    problem.requires_subscription = True
                    problem.error_message = "Requires LeetCode Premium subscription"
                    logger.warning(f"需要订阅: {problem.display_title}")
                    page.close()
                    return False
                
                # 提取信息
                problem.description = self._extract_description(page)
                problem.topics = self._extract_topics(page)
                problem.hints = self._extract_hints(page)
                problem.similar_questions = self._extract_similar_questions(page)
                
                problem.scrape_success = True
                logger.info(f"✓ 成功抓取: {problem.display_title}")
                page.close()
                return True
                
            except PlaywrightTimeout:
                logger.warning(f"页面加载超时 (尝试 {attempt + 1}/{self.max_retries}): {problem.href}")
                if page:
                    page.close()
                continue
                
            except Exception:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                error_message = repr(traceback.format_exception(exc_type, exc_value, exc_traceback))
                logger.error(f"抓取错误: {error_message}")
                problem.error_message = str(exc_value)
                if page:
                    page.close()
                
                # 最后一次尝试才返回失败
                if attempt == self.max_retries - 1:
                    return False
                continue
        
        problem.error_message = "重试次数耗尽"
        return False
    
    def _check_subscription_required(self, page: Page) -> bool:
        """
        检查是否需要订阅（改进版 - 修复误报问题）
        
        使用更精确的检测方法：
        1. 检查是否存在实际的问题内容（反向验证）
        2. 查找特定的锁定图标/元素
        3. 避免误检测页面其他部分的"premium"等词
        """
        try:
            # 方法1：检查是否有实际的问题描述内容
            # 如果能找到描述内容，说明不需要订阅
            description_selectors = [
                '[class*="elfjS"]',
                '[class*="content__"]',
                '[data-track-load="description_content"]',
                '[class*="question-content"]',
                'div[class*="_16yfq"]',
            ]
            
            has_content = False
            for selector in description_selectors:
                try:
                    element = page.query_selector(selector)
                    if element:
                        text = element.inner_text()
                        # 如果描述内容足够长，说明可以访问
                        if text and len(text) > 100:
                            logger.debug(f"找到问题描述内容 ({len(text)} 字符)，不需要订阅")
                            has_content = True
                            break
                except Exception:
                    continue
            
            # 如果找到了内容，直接返回 False（不需要订阅）
            if has_content:
                return False
            
            # 方法2：检查是否有锁定图标或明确的付费提示
            lock_selectors = [
                'svg[data-icon="lock"]',  # 锁图标
                '[class*="premium-lock"]',
                '[class*="locked-problem"]',
                'div:has-text("Unlock")',  # 包含Unlock的元素
            ]
            
            for selector in lock_selectors:
                try:
                    if page.query_selector(selector):
                        logger.debug(f"检测到锁定元素: {selector}")
                        return True
                except Exception:
                    continue
            
            # 方法3：检查页面文本中是否有明确的付费墙提示
            try:
                body_text = page.locator('body').inner_text().lower()
                
                # 只有这些明确的短语才认为需要订阅
                premium_phrases = [
                    "upgrade to unlock",
                    "this problem is available to premium",
                    "premium members only",
                    "subscribe to unlock",
                    "unlock this problem",
                ]
                
                for phrase in premium_phrases:
                    if phrase in body_text:
                        logger.debug(f"检测到付费提示: {phrase}")
                        return True
                        
            except Exception as e:
                logger.debug(f"检查付费提示失败: {e}")
            
            # 默认认为不需要订阅
            return False
            
        except Exception as e:
            logger.error(f"检查订阅状态失败: {e}")
            # 出错时默认认为不需要订阅，继续尝试提取内容
            return False
    
    def _extract_description(self, page: Page) -> Optional[str]:
        """提取问题描述（改进版）"""
        try:
            # 按优先级尝试多个选择器
            selectors = [
                # 主要内容区域
                '[class*="elfjS"]',
                '[class*="content__"]',
                '[data-track-load="description_content"]',
                
                # 问题描述特定区域
                '[class*="question-content"]',
                '[class*="description"]',
                'div[class*="_16yfq"]',
                
                # 通用选择器（最后尝试）
                'div[class*="problem"] div[class*="content"]',
                'article',
            ]
            
            for selector in selectors:
                try:
                    element = page.query_selector(selector)
                    if element:
                        text = element.inner_text()
                        # 确保提取到足够的内容
                        if text and len(text) > 50:
                            logger.debug(f"✓ 使用选择器提取描述: {selector} (长度: {len(text)})")
                            return text.strip()
                except Exception as e:
                    logger.debug(f"选择器 {selector} 失败: {e}")
                    continue
            
            # 如果所有选择器都失败，尝试更宽松的方法
            logger.warning("常规选择器未找到描述，尝试备用方法...")
            
            try:
                # 尝试获取所有可能包含描述的 div
                all_divs = page.query_selector_all('div')
                for div in all_divs:
                    text = div.inner_text()
                    # 查找包含"Example"、"Input"、"Output"等关键词的长文本
                    if (text and len(text) > 200 and 
                        any(keyword in text for keyword in ['Example', 'Input', 'Output', 'Constraints'])):
                        logger.debug(f"✓ 使用备用方法提取描述 (长度: {len(text)})")
                        return text.strip()
            except Exception as e:
                logger.debug(f"备用方法失败: {e}")
            
            logger.warning("未找到问题描述")
            return None
            
        except Exception as e:
            logger.error(f"提取描述失败: {e}")
            return None
    
    def _extract_topics(self, page: Page) -> List[str]:
        """提取主题标签"""
        try:
            selectors = [
                'a[class*="topic-tag"]',
                '[class*="tag"]',
                'a[href*="/tag/"]',
            ]
            
            topics = []
            seen = set()
            
            for selector in selectors:
                try:
                    elements = page.query_selector_all(selector)
                    for elem in elements:
                        text = elem.inner_text().strip()
                        if text and text not in seen and len(text) < 50:
                            topics.append(text)
                            seen.add(text)
                            if len(topics) >= 20:
                                break
                except Exception:
                    continue
                
                if topics:
                    break
            
            logger.debug(f"提取到 {len(topics)} 个主题")
            return topics
            
        except Exception as e:
            logger.error(f"提取主题失败: {e}")
            return []
    
    def _extract_hints(self, page: Page) -> List[str]:
        """提取提示"""
        try:
            selectors = [
                '[class*="hint"]',
                '[data-cy*="hint"]',
                'div[class*="accordion"] div[class*="content"]',
            ]
            
            hints = []
            seen = set()
            
            for selector in selectors:
                try:
                    elements = page.query_selector_all(selector)
                    for elem in elements:
                        text = elem.inner_text().strip()
                        if text and len(text) > 10 and text not in seen:
                            hints.append(text)
                            seen.add(text)
                            if len(hints) >= 10:
                                break
                except Exception:
                    continue
                
                if hints:
                    break
            
            logger.debug(f"提取到 {len(hints)} 个提示")
            return hints
            
        except Exception as e:
            logger.error(f"提取提示失败: {e}")
            return []
    
    def _extract_similar_questions(self, page: Page) -> List[SimilarQuestion]:
        """提取相似问题"""
        try:
            selectors = [
                'a[href*="/problems/"]',
            ]
            
            similar = []
            seen_urls = set()
            
            for selector in selectors:
                try:
                    elements = page.query_selector_all(selector)
                    for elem in elements:
                        href = elem.get_attribute('href')
                        if not href or '/problems/' not in href:
                            continue
                        
                        # 构建完整 URL
                        if not href.startswith('http'):
                            href = 'https://leetcode.com' + href
                        
                        if href in seen_urls:
                            continue
                        
                        title = elem.inner_text().strip()
                        if not title:
                            continue
                        
                        similar.append(SimilarQuestion(
                            title=title,
                            url=href,
                        ))
                        seen_urls.add(href)
                        
                        if len(similar) >= 10:
                            break
                except Exception:
                    continue
                
                if similar:
                    break
            
            logger.debug(f"提取到 {len(similar)} 个相似问题")
            return similar
            
        except Exception as e:
            logger.error(f"提取相似问题失败: {e}")
            return []
    
    def scrape_batch(
        self,
        problems: List[LeetCodeProblem],
        skip_subscription: bool = True
    ) -> int:
        """
        批量抓取问题
        
        Args:
            problems: 问题列表
            skip_subscription: 是否跳过需要订阅的问题
            
        Returns:
            成功抓取的数量
        """
        successful = 0
        total = len(problems)
        
        logger.info(f"开始批量抓取 {total} 个问题...")
        
        for i, problem in enumerate(problems):
            self._report_progress(
                f"抓取 {problem.display_title}",
                i + 1,
                total
            )
            
            success = self.scrape_problem(problem)
            
            if success:
                successful += 1
            elif problem.requires_subscription and skip_subscription:
                logger.info(f"跳过订阅问题: {problem.display_title}")
        
        logger.info(f"批量抓取完成: 成功 {successful}/{total}")
        return successful
    
    def debug_page_structure(self, page: Page, problem_title: str):
        """
        调试辅助：打印页面结构，帮助找到正确的选择器
        仅在开发/调试时使用
        """
        try:
            logger.info(f"\n{'='*60}")
            logger.info(f"调试页面结构: {problem_title}")
            logger.info(f"{'='*60}")
            
            # 打印所有class包含特定关键词的元素
            keywords = ['content', 'description', 'problem', 'question', 'elfjS', 'lock', 'premium']
            
            for keyword in keywords:
                try:
                    elements = page.query_selector_all(f'[class*="{keyword}"]')
                    if elements:
                        logger.info(f"\n找到 {len(elements)} 个包含 '{keyword}' 的元素:")
                        for i, elem in enumerate(elements[:3]):  # 只显示前3个
                            class_name = elem.get_attribute('class')
                            text_preview = elem.inner_text()[:80] if elem.inner_text() else ""
                            logger.info(f"  [{i+1}] class='{class_name}'")
                            if text_preview:
                                logger.info(f"      预览: {text_preview}...")
                except Exception as e:
                    logger.debug(f"查找 {keyword} 失败: {e}")
            
            logger.info(f"{'='*60}\n")
            
        except Exception as e:
            logger.error(f"调试失败: {e}")


# 使用示例
if __name__ == "__main__":
    # 配置日志
    logger.remove()
    logger.add(sys.stderr, level="INFO")
    
    # 创建测试问题
    test_problem = LeetCodeProblem(
        number=1,
        title="1. Two Sum",
        href="https://leetcode.com/problems/two-sum/",
        difficulty=Difficulty.EASY,
        completion_rate="45.3%",
    )
    
    # 使用上下文管理器
    with LeetCodeScraperPlaywright(
        headless=True,
        block_resources=True,
        min_delay=2.0,
        max_delay=4.0
    ) as scraper:
        success = scraper.scrape_problem(test_problem)
        
        if success:
            print(f"\n✓ 成功抓取: {test_problem.display_title}")
            print(f"描述长度: {len(test_problem.description or '')}")
            print(f"主题数量: {len(test_problem.topics)}")
            print(f"提示数量: {len(test_problem.hints)}")
            print(f"相似问题: {len(test_problem.similar_questions)}")
        else:
            print(f"\n✗ 抓取失败: {test_problem.error_message}")