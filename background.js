chrome.runtime.onInstalled.addListener(function() {
  chrome.contextMenus.create({
    title: "I do have this skill",
    contexts: ["selection"],
    id: "do-have",
  });
  chrome.contextMenus.create({
    title: "I don't have this skill",
    contexts: ["selection"],
    id: "dont-have",
  });
});

chrome.contextMenus.onClicked.addListener(onClickHandler);

base_url = 'http://18.191.181.111:8080'
function onClickHandler(info, tab) {
  var sText = info.selectionText;

  console.log(info.menuItemId);
  switch (info.menuItemId) {
    case "do-have":
      var myRequest = new Request(base_url + '/do-have/' + sText);
      break;
    case "dont-have":
      var myRequest = new Request(base_url + '/dont-have/' + sText);
      break;
  }
  fetch(myRequest);
  // chrome.storage.local.get(['keywords'], function(result) {
  //   console.log('Value is ' + result.keywords);
  //   var new_val = setUserPref(result.keywords, sText, 'keywords', 'word 1,word 2,word 3', ',');
  //   chrome.storage.local.set({keywords: new_val}, function() {
  //     console.log('Value is set to ' + new_val);
  //   });
  //  });
  
 
  console.log(info.menuItemId)
};

  // add more words to keyword list
//   function setUserPref(current_val, new_val, varName, defaultVal, sep){
//     if (new_val === null)  { return; }  // end execution if clicked CANCEL
// //     // prepare string of variables separated by the separator
//     if (sep && new_val){
//       var pat1 = new RegExp('\\s*' + sep + '+\\s*', 'g'); // trim space/s around separator & trim repeated separator
//       var pat2 = new RegExp('(?:^' + sep + '+|' + sep + '+$)', 'g'); // trim starting & trailing separator
//       new_val = new_val.replace(pat1, sep).replace(pat2, '');
//     }
//     new_val = new_val.replace(/\s{2,}/g, ' ').trim();    // remove multiple spaces and trim
//     return current_val + sep + new_val;
// //     // Apply changes (immediately if there are no existing highlights, or upon reload to clear the old ones)
// //     if(!document.body.querySelector(".THmo")) THmo_doHighlight(document.body);
// //     else location.reload();
//   }

const networkFilters = {
    urls: [
        "*://www.indeed.com/jobs*"
    ]
};

chrome.webRequest.onBeforeRequest.addListener((details) => {
    var parser = document.createElement('a');
    parser.href = details.url;
    url = base_url + '/jobs/' + parser.search;
    var myRequest = new Request(url);
    fetch(myRequest)  
      .then(response => {
        console.log("Fetching");
        if (response.status === 200) {
          return response.text();
        } else {
          throw new Error('Something went wrong on api server!');
        }
      }).then(function(data) {
        console.log(data);
      })
      .catch(error => {
        console.error(error);
      })
      

}, networkFilters);
