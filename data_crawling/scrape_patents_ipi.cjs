const puppeteer = require('puppeteer');
const fs = require('fs');

(async () => {
  console.log('Launching browser...');
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();

  console.log('Navigating to the target URL...');
  await page.goto('https://database.ipi.ch/database-client/search/query/patents', {
    waitUntil: 'networkidle2'
  });

  console.log('Please manually perform the necessary operations (e.g., sort by Anmeldedatum)...');
  await new Promise(resolve => setTimeout(resolve, 120000)); // 等待2分钟，手动操作

  console.log('Starting to extract data...');

  let hasNextPage = true;
  let pageCount = 0;
  const maxPages = 10920; // 设置要抓取的最大页数
  const allItems = [];
  let savedItemCount = 0;

  while (hasNextPage && pageCount < maxPages) {
    console.log(`Extracting data from page ${pageCount + 1}...`);
    await page.waitForSelector('[data-cy="result-item-wrapper"]', { timeout: 60000 });

    const items = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('[data-cy="result-item-wrapper"]')).map(item => {
        const text = item.innerText;
        const fields = text.split('\n');

        return {
          PatentName: fields[0] || 'N/A',
          Status: fields.includes('Status') ? fields[fields.indexOf('Status') + 1] : 'N/A',
          ApplicationDate: fields.includes('Anmeldedatum') ? fields[fields.indexOf('Anmeldedatum') + 1] : 'N/A',
          PatentSpecificationStatus: fields.includes('Schriftstatus') ? fields[fields.indexOf('Schriftstatus') + 1] : 'N/A',
          GeneticResources: fields.includes('Genetic resources and traditional knowledge') ? fields[fields.indexOf('Genetic resources and traditional knowledge') + 1] : 'N/A',
          TypeOfIPRight: fields.includes('Type of IP right') ? fields[fields.indexOf('Type of IP right') + 1] : 'N/A',
          IPC: fields.includes('International Patent Classification (IPC)') ? fields[fields.indexOf('International Patent Classification (IPC)') + 1] : 'N/A',
          ApplicationNumber: fields.includes('Anmeldenummer') ? fields[fields.indexOf('Anmeldenummer') + 1] : 'N/A',
          PatentNumber: fields.includes('Patentnummer') ? fields[fields.indexOf('Patentnummer') + 1] : 'N/A',
          Owner: fields.includes('Inhaber/in') ? fields[fields.indexOf('Inhaber/in') + 1] : 'N/A',
          Inventor: fields.includes('Inventor') ? fields[fields.indexOf('Inventor') + 1] : 'N/A',
        };
      });
    });

    allItems.push(...items);
    console.log(`Extracted ${items.length} items from page ${pageCount + 1}, total so far: ${allItems.length}`);

    // 每1000条保存一次数据
    if (allItems.length - savedItemCount >= 1000) {
      savedItemCount = allItems.length;
      const partialData = allItems.slice(savedItemCount - 1000, savedItemCount);
      const csvData = [
        ['Patent Name', 'Status', 'Application Date', 'Patent Specification Status', 'Genetic Resources and Traditional Knowledge', 'Type of IP Right', 'International Patent Classification (IPC)', 'Application Number', 'Patent Number', 'Owner', 'Inventor'],
        ...partialData.map(item => [
          item.PatentName, item.Status, item.ApplicationDate, item.PatentSpecificationStatus, item.GeneticResources, item.TypeOfIPRight, item.IPC, item.ApplicationNumber, item.PatentNumber, item.Owner, item.Inventor
        ])
      ].map(e => e.join(",")).join("\n");

      const filename = `patent_data_page_${pageCount}.csv`;
      fs.writeFileSync(filename, csvData);
      console.log(`Data saved to ${filename}`);
    }

    pageCount++;

    // 点击下一页
    const nextPageButton = await page.$('button.mat-mdc-tooltip-trigger.mat-mdc-paginator-navigation-next');
    if (nextPageButton) {
      console.log('Next page button found, attempting to click...');
      await page.evaluate(button => {
        button.scrollIntoView();
        button.focus();
        button.click();
      }, nextPageButton);

      await new Promise(resolve => setTimeout(resolve, 10000)); // 等待10秒以确保页面加载完成
    } else {
      hasNextPage = false;
      console.log('No more pages to navigate.');
    }
  }

  console.log('Final save of all data to CSV...');
  const csvData = [
    ['Patent Name', 'Status', 'Application Date', 'Patent Specification Status', 'Genetic Resources and Traditional Knowledge', 'Type of IP Right', 'International Patent Classification (IPC)', 'Application Number', 'Patent Number', 'Owner', 'Inventor'],
    ...allItems.map(item => [
      item.PatentName, item.Status, item.ApplicationDate, item.PatentSpecificationStatus, item.GeneticResources, item.TypeOfIPRight, item.IPC, item.ApplicationNumber, item.PatentNumber, item.Owner, item.Inventor
    ])
  ].map(e => e.join(",")).join("\n");

  fs.writeFileSync('patent_data_final.csv', csvData);
  console.log('All data saved to patent_data_final.csv');
  
  await browser.close();
})();
