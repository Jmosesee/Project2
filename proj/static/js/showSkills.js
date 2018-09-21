function sortSkills(skills, reverse) {
    var sortable = [];
    for (var s in skills) {
        sortable.push([s, skills[s]]);
    }
    
    let sorted = sortable.sort(function(a, b) {
        if (reverse) {
            return a[1] - b[1];
        } else {
            return b[1] - a[1];
        }
    });

    let sortedSkills = [];
    let sortedScores = [];
    for (s in sorted){
        sortedSkills.push(sorted[s][0]);
        sortedScores.push(sorted[s][1]);
    }
    return [sortedSkills, sortedScores];
}

function populateTable() {

    let Table = document.getElementById("ranked-table");
    let old_tbody = document.getElementById("ranked-tbody");

    fetch('https://18.220.129.126:8080/get-skills/')
      .then(function(response) {
        return response.json();
      })
      .then(function(skills) {
        let new_accordion = document.createElement("div");
        new_accordion.setAttribute("class", "panel-group");
        new_accordion.setAttribute("id", "accordion");
        new_accordion.setAttribute("role", "tablist");
        new_accordion.setAttribute("aria-multiselectable", "true");

        let rowNumber = 0 ;
        console.log("Got Data");
        for (let s in skills) {
        //for (let i=0; i<10; i++) {
            //console.log(row);
            //if (top_jobs['jobtitle'][row] != null) {
            //    console.log(top_jobs['jobtitle'][row])
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
                panel_title.innerHTML = `${skills[s]['skill_name']}`;
                panel_heading.appendChild(panel_title);
                
                let button = document.createElement("button");
                button.setAttribute("type", "button");
                button.setAttribute("class", "btn btn-info");
                button.setAttribute("id", skills[s]['skill_name'])
                button.setAttribute("onclick", "Delete(this)");
                // button.setAttribute("data-toggle", "collapse");
                // button.setAttribute("data-parent", "#accordion");
                // button.setAttribute("href", "#collapse" + rowNumber);
                // button.setAttribute("aria-expanded", "true");
                // button.setAttribute("aria-controls", "collapse" + rowNumber);
                button.innerHTML = "Delete";
                panel_title.appendChild(button);
                
                rowNumber += 1;
            //}
        } // closes for (let row in top_jobs['JobId'])
        var old_accordion = document.getElementById("accordion");
        document.body.replaceChild(new_accordion, old_accordion);
      });
  
}

function Delete(elmnt) {
    fetch('https://18.220.129.126:8080/delete-skill/' +  elmnt.id);
    location.reload();
}

function buildCharts() {
    fetch('https://18.220.129.126:8080/get-top-skills/')
      .then(function(response) {
        return response.json();
      })
      .then(function(top_skills) {
        delete top_skills['Score'];
        
        let tuple = sortSkills(top_skills, false);
        let skills = tuple[0]
        let scores = tuple[1]
        var data = [{
            x: skills,
            y: scores,
            type: 'bar'
        }];
          
        var layout = {
            height: 400,
            width: 500
        };
        Plotly.newPlot('do-have-chart', data, layout);
      })
      
    fetch('https://18.220.129.126:8080/get-neg-skills/')
      .then(function(response) {
        return response.json();
      })
      .then(function(top_skills) {
        delete top_skills['Score'];
        
        let tuple = sortSkills(top_skills, true);
        let skills = tuple[0]
        let scores = tuple[1]
        var data = [{
            x: skills,
            y: scores,
            type: 'bar'
        }];
          
        var layout = {
            height: 400,
            width: 500
        };
        Plotly.newPlot('dont-have-chart', data, layout);
      })
}

populateTable();
buildCharts();
