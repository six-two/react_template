const DATA = __I18N_JSON__;
const DEFAULT_LANG = "en";

console.debug("Language data:", DATA);

const applyLang = (lang) => {
    const data = DATA[lang] || {};
    console.log(`Applying language: ${lang}`);
    for (const [id, translations] of Object.entries(DATA)) {
        elem = document.getElementById(id);
        if (elem) {
            let translation = "<ERROR>";
            try {
                translation = translations[lang] || translations[DEFAULT_LANG] || "<Missing translation>";
                console.debug(`Translation for "${id}" is "${translation}"`);
            } catch (e) {
                console.warn(e);
            }

            elem.innerHTML = translation;
            if (id === "page-title") {
                // Set the window title and make the page-title element resizeable again
                document.title = translation;
                try {
                    textFit(document.getElementById(id));
                } catch (error) {
                    console.warn("Could not make title auto resizeable");
                }
            }
        } else {
            console.debug(`Element "${id}" does not exist`);
        }
    }
}

const getLang = () => {
    const params = new URLSearchParams(window.location.search);
    return params.get("lang") || DEFAULT_LANG;
}


let old_lang = "";

const updateLang = () => {
    const lang = getLang();
    if (lang !== old_lang) {
        old_lang = lang;
        applyLang(lang);
    }
}

// Repeatedly check url lang, and update elements if it changes
setInterval(updateLang, 100);