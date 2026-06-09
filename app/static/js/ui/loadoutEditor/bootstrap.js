(function () {
    const LoadoutEditor = window.LoadoutEditor;

    function attachSaveListener() {
        const saveButton = document.querySelector(".loadout-save-button");

        if (!saveButton || LoadoutEditor.state.hasSaveListener) return;

        saveButton.addEventListener("pointerdown", LoadoutEditor.saveLoadoutConfiguration);
        LoadoutEditor.state.hasSaveListener = true;
    }

    function attachTitleEditorListeners() {
        const titleEditButton = document.querySelector(".loadout-title-edit-button");
        const titleHeader = LoadoutEditor.getLoadoutTitleElement();

        if (!titleEditButton || !titleHeader || LoadoutEditor.state.hasTitleListeners) return;

        titleEditButton.addEventListener("click", function () {
            titleHeader.setAttribute("contenteditable", "true");
            titleHeader.setAttribute("spellcheck", "false");
            titleHeader.focus();

            const range = document.createRange();
            const selection = window.getSelection();

            range.selectNodeContents(titleHeader);
            range.collapse(false);

            selection.removeAllRanges();
            selection.addRange(range);
        });

        titleHeader.addEventListener("blur", function () {
            titleHeader.removeAttribute("contenteditable");
        });

        titleHeader.addEventListener("keydown", function (event) {
            if (event.key === "Enter") {
                event.preventDefault();
                titleHeader.blur();
            }

            if (event.key === "Escape") {
                event.preventDefault();
                titleHeader.blur();
            }
        });

        LoadoutEditor.state.hasTitleListeners = true;
    }

    function startLoadoutEditor() {
        LoadoutEditor.attachEditorDragListeners();
        attachSaveListener();
        attachTitleEditorListeners();
        LoadoutEditor.registerAllAgents();
    }

    Object.assign(LoadoutEditor, {
        attachSaveListener,
        attachTitleEditorListeners,
        startLoadoutEditor
    });

    window.showLoadoutEditor = function (loadoutCardElement) {
        return LoadoutEditor.showLoadoutEditor(loadoutCardElement);
    };

    window.startLoadoutEditor = function () {
        return LoadoutEditor.startLoadoutEditor();
    };

    window.openSavedLoadout = function (loadoutCardElement) {
        return LoadoutEditor.openSavedLoadout(loadoutCardElement);
    };

    window.addNewAgent = function () {
        return LoadoutEditor.addNewAgent();
    };

    attachSaveListener();
    attachTitleEditorListeners();
})();
