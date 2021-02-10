const conf = require('config');
const playwright = require('playwright');
const $ = require('jquery');
const jsdom = require("jsdom");
const Log4js = require("log4js");
Log4js.configure("./src/log-config.json");
const axios = require('axios');
const fs = require('fs');
// mkdir.js
const makeDir = require("make-dir");
const dayjs = require("dayjs");
const logger = Log4js.getLogger("system");
const errorLogger = Log4js.getLogger("error");

global.URL = require('url').URL;
const imagePath = conf.get("system.imagePath")

exports.scrapingYahooAuctionPage = async (page) => {
    try {
        logger.info("Scraping YahooAuctionPage")
        let splitUrl = page.url().split("/")
        let productNumber = splitUrl.pop()
        let nowTime = dayjs().format("YYYYMMDD-HH:mm:ss")
        logger.info(page.url())
        logger.info(`productNumber : ${productNumber}`)
        // YahooActionページの商品情報の取得
        let productInfo = await page.evaluate(() => {
            let title = document.querySelector('.ProductTitle__text').textContent
            let price = document.querySelector('.Price__value').textContent
            price = price.match(/(\d|,)+?円/g)
            let stock = document.querySelector('.ProductDetail__description').textContent
            stock.replace("：", "")
            let imageElements = document.querySelectorAll('.ProductImage__link > img')
            let imageUrls = []
            imageElements.forEach(
                function(element) {
                    imageUrls.push(element.src)
                }
            )
            return {title: title, price: price, stock: stock, imageUrls: imageUrls}
        })
        // 画像ダウンロード
        const downloadDir = `${imagePath}/${productNumber}`
        makeDir(downloadDir).then(path => {
            console.log(path);
            // 作成されたディレクトリのパスが表示されます
          });          
        let num = 1
        productInfo.imageUrls.forEach(
            async function(url) {
                logger.info('-----------------------')
                logger.info(url)
                logger.info('-----------------------')
                const response = await axios.get(url, {responseType: 'arraybuffer'})
                await fs.writeFileSync(`${downloadDir}/product_image_${nowTime}_${num}.jpg`, new Buffer.from(response.data), 'binary')
                num = num + 1
            }
        )
        await logger.info(productInfo)
    } catch (e) {
        logger.error(e)
    } finally {

    }
}