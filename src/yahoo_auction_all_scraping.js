const conf = require('config');
const playwright = require('playwright');
const $ = require('jquery');
const jsdom = require("jsdom");
const Log4js = require("log4js");
Log4js.configure("./src/log-config.json");
const axios = require('axios');
const fs = require('fs');
const scraping = require('./scraping.js');

const logger = Log4js.getLogger("system");
const errorLogger = Log4js.getLogger("error");
const imagePath = conf.get("system.imagePath")

global.URL = require('url').URL;

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("scrapingForm").onsubmit = () => {
        var inputUrl = $("#inputUrl").val()
        logger.info(inputUrl)
        main(inputUrl)
        return false;
    };
});
const main = async (url) => {
    try {
        logger.info("Scraping scrapingAllYahooAuction")
        const browser = await playwright[conf.playwright.browserType].launch({ headless: conf.playwright.isHeadless})
        const context = await browser.newContext({viewport:{ width: 1420, height: 720 } })
        const page = await context.newPage()
        await page.setViewportSize({ width: 1420, height: 692 })
        context.setDefaultTimeout(conf.playwright.defaultTimeout)

        logger.info("Scraping Start")
        await page.goto(url)
        await page.screenshot({ path:`${imagePath}/ヤフオク一覧_画面表示.png` })
        let productUrls = await page.evaluate(() => {
            let productElements = document.querySelectorAll('.Product__titleLink')
            let productUrls = []
            productElements.forEach(
                function(element) {
                    productUrls.push(element.href)
                }
            )
            return productUrls
        })

        // 商品情報取得処理
        let i = 0
        for (const url of productUrls) {
            i++
            await page.goto(url)
            await page.screenshot({ path:`${imagePath}/${i}_画面表示.png` })
            await scraping.scrapingYahooAuctionPage(page)
        }

        // let i = 0
        // for (const url of urls) {
        //     i++
        //     await page.goto(url)
        //     await page.screenshot({ path: i + `_画面表示.png` })
        //     let productInfo = await page.evaluate(() => {
        //         let title = document.querySelector('.ProductTitle__text').textContent
        //         let price = document.querySelector('.Price__value').textContent
        //         price = price.match(/(\d|,)+?円/g)
        //         let stock = document.querySelector('.ProductDetail__description').textContent
        //         stock.replace("：", "")
        //         return {title: title, price: price, stock: stock}
        //     })
        //     await logger.info(productInfo)
        // }
        logger.info(productUrls)
        logger.info("Scraping End")
        await browser.close()

    } catch (e) {
        logger.error(e)
    } finally {

    }
}