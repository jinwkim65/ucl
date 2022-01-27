document.addEventListener('DOMContentLoaded', function() {
    let input = document.querySelector('#tourneys');
    let year = document.querySelector('#years');
    let level = document.querySelector('#levels');
    let current_level = "Advanced"
    input.addEventListener('change', async function() {
        if (input.value === "Elite" || input.value === "Premier") {
            current_level = "Advanced%2B";
        }
        let response = await fetch("/find?t=" + input.value.toLowerCase() + "&level=" + current_level);
        let html = await response.text();
        let new_html = html.substring(html.indexOf("years") + 7, html.indexOf("btn btn-primary") - 76);
        let new_html_2 = html.substring(html.indexOf("levels") + 17, html.indexOf("tourneys") - 100);
        console.log(level.innerHTML.trim(), level.innerHTML.trim().length)
        console.log(new_html_2.trim(), new_html_2.trim().length)
        if (level.innerHTML.trim().length - 6 != new_html_2.trim().length) {
            level.innerHTML = new_html_2;
        }
        year.innerHTML = new_html;
    });
    level.addEventListener('change', async function() {
        current_level = level.value;
        console.log(level.value);
        let response = await fetch("/find?t=" + input.value.toLowerCase() + "&level=" + current_level);
        let html = await response.text();
        let new_html = html.substring(html.indexOf("years") + 7, html.indexOf("btn btn-primary") - 76);
        year.innerHTML = new_html;
    });
});