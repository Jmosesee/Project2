// ==UserScript==
// @name          Text Highlighter - Dynamic
// @namespace     erosman
// @author        erosman and Jefferson "jscher2000" Scher
// @version       1.7mo
// @description   Highlights User-defined Text
// @include       https://greasyfork.org/*
// @grant         GM_registerMenuCommand
// @grant         GM_setValue
// @grant         GM_getValue
// ==/UserScript==

/* --------- Note ---------
  This script highlights User-defined case-insensitive Text on a page.

  TO INCLUDE SITES (only Greasy Fork is initially included):

  Go to Add-ons - User Scripts ('Ctrl+ Shift + a' on Firefox)
  Click on the Script's Option
  Under User Settings Tab, Add Included/Excluded Pages that you want the script to run on
  Click OK

  Setting Keywords & Highlight Style:
  Click on drop-down triangle next to the GreaseMonkey Icon
  User Scripts Commands...

      Set Keywords
      Input keywords separated by comma
      Example: word 1,word 2,word 3

      Set Highlight Style
      Input the Highlight Style (use proper CSS)
      Example: color: #f00; font-weight: bold; background-color: #ffe4b5;

  Note: If you find that another script clashes with this script, set Text Highlighter to Execute first.
  Go to Add-ons - User Scripts ('Ctrl+ Shift + a' on Firefox)
  Right Click on the Script
  On the context menu click: Execute first

  On Add-ons - User Scripts, you can also Click on the Execution Order (top Right) and
  change the execution order so that Text Highlighter runs before those scripts that clashes with it.


  --------- History ---------
  1.7mo Added MutationObserver (Jefferson "jscher2000" Scher)
  1.7 Changed script from matching whole words to do partial word match 
      similar to browser's FIND + escaped RegEx Quantifiers in keywords
  1.6 Code Improvement, using test()
  1.5 Code Improvement
  1.4 Code Improvement + Added support for non-English Words
  1.3 Code Improvement, 10x speed increase
  1.2 Added User Script Commands, script can now be auto-updated without losing User Data
  1.1 Total Code rewrite, Xpath pattern
  1.0 Initial release
*/

(function() { // anonymous function wrapper, used for error checking & limiting scope
  'use strict';
  var do_have_skill = [];
  var dont_have_skill = [];
  
  // if (window.self !== window.top) { return; } // end execution if in a frame
  
  // setUserPref(
  // 'highlightStyle',
  // 'color: #f00; background-color: #ffebcd;',
  // 'Set Highlight Style',
  // 'Set the Highlight Style (use proper CSS)\r\n\r\nExample:\r\ncolor: #f00; font-weight: bold; background-color: #ffe4b5;'
  // );
  
  // Add MutationObserver to catch content added dynamically
  // var THmo_MutOb = (window.MutationObserver) ? window.MutationObserver : window.WebKitMutationObserver;
  // if (THmo_MutOb){
  //   var THmo_chgMon = new THmo_MutOb(function(mutationSet){
  //     mutationSet.forEach(function(mutation){
  //       for (var i=0; i<mutation.addedNodes.length; i++){
  //         if (mutation.addedNodes[i].nodeType == 1){
  //           THmo_doHighlight(mutation.addedNodes[i]);
  //         }
  //       }
  //     });
  //   });
  //   // attach chgMon to document.body
  //   var opts = {childList: true, subtree: true};
  //   THmo_chgMon.observe(document.body, opts);
  // }
  // Main workhorse routine
  function THmo_doHighlight(el){
        
    if(!do_have_skill)  { return; }  // end execution if not found
    var do_haveStyle = "color:#00f; font-weight:bold; background-color: #0f0;"
    var dont_haveStyle = "color:#fcc; font-weight:bold; background-color: #f00;"
    var rQuantifiers = /[-\/\\^$*+?.()|[\]{}]/g;
    //keywords = keywords.replace(rQuantifiers, '\\$&').split(',').join('|');

    var modified_do_have = []
    var modified_dont_have = []
    do_have_skill.forEach(s => modified_do_have.push('[' + s[0].toUpperCase() + s[0].toLowerCase() + ']' + s.slice(1) + String.raw`[^\w]`));   
    dont_have_skill.forEach(s => modified_dont_have.push('[' + s[0].toUpperCase() + s[0].toLowerCase() + ']' + s.slice(1) + String.raw`[^\w]`));   
    console.log(modified_do_have)
    var joined_do_have_skill = modified_do_have.join('|');
    var joined_dont_have_skill = modified_dont_have.join("|");
    //console.log(joined_keywords);
    var do_have_pat = new RegExp('(' + joined_do_have_skill + ')', 'g');
    var dont_have_pat = new RegExp('(' + joined_dont_have_skill + ')', 'g');
    var span = document.createElement('span');
    // getting all text nodes with a few exceptions
    var snapElements = document.evaluate(
        './/text()[normalize-space() != "" ' +
        'and not(ancestor::style) ' +
        'and not(ancestor::script) ' +
        'and not(ancestor::textarea) ' +
        'and not(ancestor::code) ' +
        'and not(ancestor::pre)]',
        el, null, XPathResult.UNORDERED_NODE_SNAPSHOT_TYPE, null);
    
    if (!snapElements.snapshotItem(0)) { return; }  // end execution if not found
    
    for (var i = 0, len = snapElements.snapshotLength; i < len; i++) {
      var node = snapElements.snapshotItem(i);
      // check if it contains the keywords
      if (do_have_pat.test(node.nodeValue) || dont_have_pat.test(node.nodeValue)) {
        // check that it isn't already highlighted
        if (node.className != "THmo" && node.parentNode.className != "THmo"){
          // create an element, replace the text node with an element
          var sp = span.cloneNode(true);
          sp.innerHTML = node.nodeValue.replace(dont_have_pat, '<span style="' + dont_haveStyle + '" class="THmo">$1</span>')
                                        .replace(do_have_pat, '<span style="' + do_haveStyle + '" class="THmo">$1</span>');
          node.parentNode.replaceChild(sp, node);
        }
      }
    }
  }
  // first run
  // Todo: Keep the skills list updated as the user adds new skills
  function getKeywords(){
    var myRequest = new Request('https://18.220.129.126:8080/get-skills/');
    fetch(myRequest)  
    .then(response => {
      if (response.status === 200) {
        return response.json();
      } else {
        throw new Error('Something went wrong on api server!');
      }
    })
    .then(function(data) {
      console.log("Adding new keywords");
      do_have_skill = [];
      dont_have_skill = [];
      data.forEach(d => {
        if (d.have){
          do_have_skill.push(d.skill_name);
        } else {
          dont_have_skill.push(d.skill_name);
        }
      })
      console.log(dont_have_skill);
    }).catch(error => {
      console.error(error);
    })
    .then(function(data){
      if ((do_have_skill.length > 0) && (dont_have_skill.length > 0)) {
        console.log("Applying highlights");
        THmo_doHighlight(document.body);
      }
    })
  }
  getKeywords();
})();


