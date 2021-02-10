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
        console.log("Form Submit!!");
        var inputUrls = $("input.inputUrl").map(function (index, el) {return $(this).val()})
        logger.info(inputUrls)
        main(inputUrls)
        // document.querySelectorAll('input.inputUrl')
        // .forEach((element) => {
        //     logger.info(element.value);
        //     scrapingYahooAuction(element.value);
        // })
        return false;
    };
});
const main = async (urls) => {
    try {
        const browser = await playwright[conf.playwright.browserType].launch({ headless: conf.playwright.isHeadless})
        const context = await browser.newContext({viewport:{ width: 1420, height: 720 } })
        const page = await context.newPage()
        await page.setViewportSize({ width: 1420, height: 692 })
        context.setDefaultTimeout(conf.playwright.defaultTimeout)

        logger.info("main Start")
        let i = 0
        for (const url of urls) {
            i++
            await page.goto(url)
            await page.screenshot({ path:`${imagePath}/${i}_画面表示.png`})
            await scraping.scrapingYahooAuctionPage(page)
            // ページ遷移されたかを待つ
            // await page.waitForNavigation()
            
            // ページ遷移の待機を要素指定で待つ
            // await page.waitForSelector('button.login-btn')
            
            // 入力したいときの参考
            // await page.fill('input[name="password"]', password)
            
            // クリックしたいときの参考
            // await page.click('button.login-btn')
        }
        logger.info("main End")
        await browser.close()

    } catch (e) {
        logger.error(e)
    } finally {

    }
}