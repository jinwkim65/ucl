document.addEventListener('DOMContentLoaded', function() {
    let tournament = document.querySelector('#tourneys');
    let year = document.querySelector('#years');
    let level = document.querySelector('#level');

    // Tournament is updated
    tournament.addEventListener('change', async function() {
        let response = await fetch("/?tournament=" + tournament.value);
        let html = await response.text();

        // Retrieve HTML for levels and years for that tournament
        let level_html = html.substring(html.indexOf("<!--LEVEL_START-->") + 18, html.indexOf("<!--LEVEL_END-->") + 16);
        let year_html = html.substring(html.indexOf("<!--YEAR_START-->") + 17, html.indexOf("<!--YEAR_END-->") +15);

        // Change HTML to reflect its years and levels
        level.innerHTML = level_html;
        year.innerHTML = year_html;
    });

    // Level is updated
    level.addEventListener('change', async function() {
        current_level = level.value;
        let response = await fetch("/?tournament=" + tournament.value + "&level=" + current_level);
        let html = await response.text();
        let year_html = html.substring(html.indexOf("<!--YEAR_START-->") + 17, html.indexOf("<!--YEAR_END-->") +15);
        year.innerHTML = year_html;
    });

    // Year is updated
    year.addEventListener('change', async function() {
        current_year = year.value;
        let response = await fetch("/?tournament=" + tournament.value + "&year=" + current_year);
        let html = await response.text();
        let level_html = html.substring(html.indexOf("<!--LEVEL_START-->") + 18, html.indexOf("<!--LEVEL_END-->") + 16);
        level.innerHTML = level_html;
    });
});