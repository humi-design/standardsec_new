// Load search data once
let searchData = [];

fetch('search-data.json')
  .then(response => response.json())
  .then(data => {
    searchData = data;
  });

// Function to handle search
function performSearch(query) {
  query = query.toLowerCase();
  let results = searchData.filter(page =>
    page.title.toLowerCase().includes(query) ||
    page.content.toLowerCase().includes(query)
  );

  displayResults(results);
}

// Display results in container
function displayResults(results) {
  let container = document.getElementById("search-results");
  container.innerHTML = "";

  if (results.length === 0) {
    container.innerHTML = "<p>No results found</p>";
    return;
  }

  results.forEach(r => {
    let item = document.createElement("div");
    item.innerHTML = `<a href="${r.url}"><strong>${r.title}</strong></a><p>${r.content.substring(0, 100)}...</p>`;
    container.appendChild(item);
  });
}
