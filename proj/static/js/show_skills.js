function populateTable() {

    let Table = document.getElementById("ranked-table");
    let old_tbody = document.getElementById("ranked-tbody");

    console.log("Populating Table");
    fetch('https://18.220.129.126:8080/get-skills/')
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
                panel_title.setAttribute("class", "panel_title");
                // Todo: consider breaking this down
                panel_title.innerHTML = `Skill ${rowNumber+1}`;
                panel_heading.appendChild(panel_title);
                
                let button = document.createElement("button");
                button.setAttribute("type", "button");
                button.setAttribute("class", "btn btn-info");
                // button.setAttribute("data-toggle", "collapse");
                // button.setAttribute("data-parent", "#accordion");
                // button.setAttribute("href", "#collapse" + rowNumber);
                // button.setAttribute("aria-expanded", "true");
                // button.setAttribute("aria-controls", "collapse" + rowNumber);
                button.innerHTML = "Delete";
                panel_title.appendChild(button);
                
                rowNumber += 1;
            }
        } // closes for (let row in top_jobs['JobId'])
        var old_accordion = document.getElementById("accordion");
        document.body.replaceChild(new_accordion, old_accordion);
      });
}

populateTable();
