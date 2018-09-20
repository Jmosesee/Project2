(function populateTable() {

    let Table = document.getElementById("ranked-table");
    let old_tbody = document.getElementById("ranked-tbody");

    fetch('https://18.191.252.14:8080/get-top-jobs/')
      .then(function(response) {
        return response.json();
      })
      .then(function(top_jobs) {
        let new_tbody = document.createElement("tbody")
        new_tbody.setAttribute("id", "ranked-tbody");
        let rowNumber = 0 
        for (let row in top_jobs['JobId']) {
            if (top_jobs['jobtitle'][row] != null) {
                // Create an empty <tr> element and add it to the table:
                let tableRow = new_tbody.insertRow(rowNumber);
                let cell = tableRow.insertCell(0);
                cell.style.border = '1px solid black';
                cell.innerHTML = 
                    `<h2 class="jobtitle">
                        <a href=${top_jobs['link'][row]}>${top_jobs['jobtitle'][row]}</a>
                    </h2>
                    <h3 class="company">${top_jobs['company'][row]}</h3>
                    <h4 class="location">${top_jobs['location'][row]}</h4>
                    <div class="summary">${top_jobs['job_summary'][row].slice(0, 200)}...</div>`;
                rowNumber += 1;
            }
       }
       Table.replaceChild(new_tbody, old_tbody);
      });
  
})()
