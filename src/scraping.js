const conf = require('config');
const playwright = require('playwright');
const $ = require('jquery');
const jsdom = require("jsdom");
const Log4js = require("log4js");
Log4js.configure("./src/log-config.json");

const logger = Log4js.getLogger("system");
const errorLogger = Log4js.getLogger("error");

global.URL = require('url').URL;

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("scrapingForm").onsubmit = () => {
        console.log("Form Submit!!");
        var inputUrls = $("input.inputUrl").map(function (index, el) {return $(this).val()})
        logger.info(inputUrls)
        scrapingYahooAuction(inputUrls)
        // document.querySelectorAll('input.inputUrl')
        // .forEach((element) => {
        //     logger.info(element.value);
        //     scrapingYahooAuction(element.value);
        // })
        return false;
    };
});
const scrapingYahooAuction = async (urls) => {
    try {
        const browser = await playwright[conf.playwright.browserType].launch({ headless: conf.playwright.isHeadless})
        const context = await browser.newContext({viewport:{ width: 1420, height: 720 } })
        const page = await context.newPage()
        await page.setViewportSize({ width: 1420, height: 692 })
        context.setDefaultTimeout(conf.playwright.defaultTimeout)

        logger.info("Scraping Start")
        let i = 0
        for (const url of urls) {
            i++
            await page.goto(url)
            await page.screenshot({ path: i + `_画面表示.png` })
            let productInfo = await page.evaluate(() => {
                let title = document.querySelector('.ProductTitle__text').textContent
                let price = document.querySelector('.Price__value').textContent
                price = price.match(/(\d|,)+?円/g)
                let stock = document.querySelector('.ProductDetail__description').textContent
                stock.replace("：", "")
                return {title: title, price: price, stock: stock}
            })
            await logger.info(productInfo)
            // ページ遷移されたかを待つ
            // await page.waitForNavigation()
            
            // ページ遷移の待機を要素指定で待つ
            // await page.waitForSelector('button.login-btn')
            
            // 入力したいときの参考
            // await page.fill('input[name="password"]', password)
            
            // クリックしたいときの参考
            // await page.click('button.login-btn')
        }
        logger.info("Scraping End")
        await browser.close()

    } catch (e) {
        logger.error(e)
    } finally {

    }
}