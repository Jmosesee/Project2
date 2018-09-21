function populateTable() {

    let Table = document.getElementById("ranked-table");
    let old_tbody = document.getElementById("ranked-tbody");

    fetch('https://18.220.129.126:8080/get-top-jobs/')
      .then(function(response) {
        return response.json();
      })
      .then(function(top_jobs) {
        let new_accordion = document.createElement("div");
        new_accordion.setAttribute("class", "panel-group");
        new_accordion.setAttribute("id", "accordion");
        new_accordion.setAttribute("role", "tablist");
        new_accordion.setAttribute("aria-multiselectable", "true");
        
        let rowNumber = 0 ;
        for (let row in top_jobs['JobId']) {
            if (top_jobs['jobtitle'][row] != null) {
                let panel = document.createElement("div");
                panel.setAttribute("class", "panel panel-default");
                new_accordion.appendChild(panel);
                
                let panel_heading = document.createElement("div");
                panel_heading.setAttribute("class", "panel-heading");
                panel_heading.setAttribute("role", "tab");
                panel_heading.setAttribute("id", "heading" + rowNumber);
                panel.appendChild(panel_heading);
                
                let panel_title = document.createElement("h4");
                panel_title.setAttribute("class", "panel-title");
                // Todo: consider breaking this down
                panel_title.innerHTML = `<a href=${top_jobs['link'][row]} target="_blank">${top_jobs['jobtitle'][row]}</a>`;
                panel_heading.appendChild(panel_title);
                
                let button = document.createElement("button");
                button.setAttribute("type", "button");
                button.setAttribute("class", "btn btn-info");
                button.setAttribute("data-toggle", "collapse");
                button.setAttribute("data-parent", "#accordion");
                button.setAttribute("href", "#collapse" + rowNumber);
                button.setAttribute("aria-expanded", "true");
                button.setAttribute("aria-controls", "collapse" + rowNumber);
                button.innerHTML = "Toggle Summary";
                panel_title.appendChild(button);
                
                let teaser = document.createElement("div");
                teaser.setAttribute("class", "panel-teaser panel-body");
                teaser.innerHTML = 
                    `${top_jobs['company'][row]}<br>
                    ${top_jobs['location'][row]}`;
                panel.appendChild(teaser);
                
                let panel_collapse = document.createElement("div");
                panel_collapse.setAttribute("id", "collapse" + rowNumber);
                panel_collapse.setAttribute("class", "panel-collapse collapse");
                panel_collapse.setAttribute("role", "tabpanel");
                panel_collapse.setAttribute("aria-labelledby", "heading" + rowNumber);
                panel.appendChild(panel_collapse);
                
                let panel_body = document.createElement("div");
                panel_body.setAttribute("class", "panel-body");
                panel_body.innerHTML = `${top_jobs['job_summary'][row]}`;
                panel_collapse.appendChild(panel_body);
                
                // // Create an empty <tr> element and add it to the table:
                // let tableRow = new_tbody.insertRow(rowNumber);
                // let cell = tableRow.insertCell(0);
                // cell.style.border = '1px solid black';
                // cell.innerHTML = 
                //     `<h2 class="jobtitle">
                //         <a href=${top_jobs['link'][row]}>${top_jobs['jobtitle'][row]}</a>
                //     </h2>
                //     <h3 class="company">${top_jobs['company'][row]}</h3>
                //     <h4 class="location">${top_jobs['location'][row]}</h4>
                //     <div class="summary">${top_jobs['job_summary'][row].slice(0, 300)}...</div>`;
                rowNumber += 1;
            }
        } // closes for (let row in top_jobs['JobId'])
        var old_accordion = document.getElementById("accordion");
        document.body.replaceChild(new_accordion, old_accordion);
      });
  
}

populateTable();
