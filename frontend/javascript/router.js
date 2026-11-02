// Loads each screen's HTML file and JS file ONCE, then switches screens without reloading.
// URLs: index.html#home, index.html#grading, index.html#about
(() => {
    const DEFAULT_SCREEN = "home";

    // name -> container id in index.html, the HTML partial to load, and the JS file to run (or null)
    const SCREENS = {
        home:    { container: "home-screen",           html: "home.html",           js: "javascript/home.js" },
        grading: { container: "grading-scheme-screen", html: "grading_scheme.html", js: "javascript/grading_scheme.js" },
        about:   { container: "about-screen",          html: "about.html",          js: null },
    };
    const navLinks = document.querySelectorAll(".navbar-link[data-screen]");

    async function loadHtml(screen) {
        const response = await fetch(screen.html);
        if (!response.ok) throw new Error(`Could not load ${screen.html} (${response.status})`);
        document.getElementById(screen.container).innerHTML = await response.text();
    }

    // Scripts are added one after another, only after ALL the HTML is in the page,
    // because they look up elements by id as soon as they run.
    function loadScript(src) {
        return new Promise((resolve, reject) => {
            const script = document.createElement("script");
            script.src = src;
            script.onload = resolve;
            script.onerror = () => reject(new Error(`Could not load ${src}`));
            document.body.appendChild(script);
        });
    }

    function showScreen() {
        const requested = location.hash.replace("#", "");
        const name = requested in SCREENS ? requested : DEFAULT_SCREEN;

        for (const [screenName, screen] of Object.entries(SCREENS)) {
            document.getElementById(screen.container).hidden = screenName !== name;
        }
        for (const link of navLinks) {
            link.classList.toggle("is-active", link.dataset.screen === name);
        }
        window.scrollTo(0, 0);
    }

    async function start() {
        try {
            await Promise.all(Object.values(SCREENS).map(loadHtml));
            for (const screen of Object.values(SCREENS)) {
                if (screen.js) await loadScript(screen.js);
            }
        } catch (error) {
            console.error(error);
            document.getElementById("app").textContent = "Could not load the app. Check the Console for details.";
            return;
        }
        window.addEventListener("hashchange", showScreen);
        showScreen();
    }

    start();
})();