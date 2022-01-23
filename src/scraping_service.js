const conf = require('config');
const Log4js = require("log4js");
Log4js.configure("./src/log-config.json");
const {spawn} = require('child_process');
var {PythonShell} = require('python-shell');

exports.scraping = async (args) => {
    logger.info(args)
    if (!args) {
        return false;
    }
    // install必要なモジュール
    // bs4,lxml,requests,selenium、chromedriver_binary
    const target = `${__dirname}/${conf.get("system.scrapingTool")}`
    // const command = `${target} ${args.join(' ')}`
    // const command = args
    // const process = spawn('python', command)
    // process.stdout.on('data', (data) => {
    //     let dataString = data.toString()
    //     logger.info(dataString)
    // });
    const options = {
        args : args
    }
    // let pyShell = new PythonShell(target, options);
    let pyShell = new PythonShell(target);
    pyShell.send(options); 
    pyShell.on('message', function(message) {
      logger.info(message)
    })
}