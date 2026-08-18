/*
========================================================
PHOENIX VISION AI
Phoenix Admin — Account Requests
========================================================
*/

document.addEventListener(
    "DOMContentLoaded",
    () => {

        const list =
            document.getElementById(
                "requests-list"
            );

        const count =
            document.getElementById(
                "pending-count"
            );

        const noSelection =
            document.getElementById(
                "no-selection"
            );

        const form =
            document.getElementById(
                "admin-request-form"
            );

        const requestId =
            document.getElementById(
                "request-id"
            );

        const fullName =
            document.getElementById(
                "request-full-name"
            );

        const status =
            document.getElementById(
                "request-status"
            );

        const photoInput =
            document.getElementById(
                "user-photo"
            );

        const photoPreview =
            document.getElementById(
                "photo-preview"
            );

        const assignedUsername =
            document.getElementById(
                "assigned-username"
            );

        const assignedRole =
            document.getElementById(
                "assigned-role"
            );

        const accessLevel =
            document.getElementById(
                "access-level"
            );

        const accountExpiry =
            document.getElementById(
                "account-expiry"
            );

        const message =
            document.getElementById(
                "admin-message"
            );

        const editButton =
            document.getElementById(
                "edit-request"
            );

        const saveButton =
            document.getElementById(
                "save-request"
            );

        const credentialsBox =
            document.getElementById(
                "credentials-box"
            );

        const createdUsername =
            document.getElementById(
                "created-username"
            );

        const temporaryPassword =
            document.getElementById(
                "temporary-password"
            );

        const copyCredentials =
            document.getElementById(
                "copy-credentials"
            );


        const fields = {

            nom:
                document.getElementById(
                    "admin-nom"
                ),

            postnom:
                document.getElementById(
                    "admin-postnom"
                ),

            prenom:
                document.getElementById(
                    "admin-prenom"
                ),

            sexe:
                document.getElementById(
                    "admin-sexe"
                ),

            date_naissance:
                document.getElementById(
                    "admin-naissance"
                ),

            email:
                document.getElementById(
                    "admin-email"
                ),

            telephone:
                document.getElementById(
                    "admin-telephone"
                ),

            organisation:
                document.getElementById(
                    "admin-organisation"
                ),

            matricule:
                document.getElementById(
                    "admin-matricule"
                ),

            departement:
                document.getElementById(
                    "admin-departement"
                ),

            fonction:
                document.getElementById(
                    "admin-fonction"
                ),

            site_affectation:
                document.getElementById(
                    "admin-site"
                ),

            responsable:
                document.getElementById(
                    "admin-responsable"
                ),

            motif:
                document.getElementById(
                    "admin-motif"
                )

        };

        const missingFields =
            Object.entries(
                fields
            )
            .filter(
                ([name, field]) =>
                    field === null
            )
            .map(
                ([name]) =>
                    name
            );


        if(missingFields.length > 0){

            console.error(
                "Phoenix Admin - Champs HTML manquants :",
                missingFields
            );

        }


        let requests = [];

        let selected = null;

        let editMode = false;


        function setEditMode(
            enabled
        ){

            editMode = enabled;


            Object.values(
                fields
            ).forEach(
                field => {

                    /*
                    Protection :
                    si un champ HTML manque,
                    Phoenix Admin ne plante plus.
                    */

                    if(!field){

                        return;

                    }


                    field.disabled =
                        !enabled;

                }
            );


            editButton.textContent =
                enabled
                ?
                "Annuler"
                :
                "Modifier";

        }


        function renderPhoto(
            path
        ){

            photoPreview.innerHTML =
                "";


            if(!path){

                photoPreview.innerHTML =
                    "<span>PHOTO</span>";

                return;

            }


            const image =
                document.createElement(
                    "img"
                );


            image.src = path;

            image.alt =
                "Photo utilisateur";


            photoPreview.appendChild(
                image
            );

        }


        function fillField(
            name,
            value
        ){

            if(fields[name]){

                fields[name].value =
                    value || "";

            }

        }


        function selectRequest(
            data
        ){

            selected = data;


            credentialsBox.classList.add(
                "hidden"
            );


            requestId.value =
                data.request_id;


            fullName.textContent =
                [
                    data.nom,
                    data.postnom,
                    data.prenom
                ]
                .filter(Boolean)
                .join(" ");


            status.textContent =
                data.status || "PENDING";


            fillField(
                "nom",
                data.nom
            );

            fillField(
                "postnom",
                data.postnom
            );

            fillField(
                "prenom",
                data.prenom
            );

            fillField(
                "sexe",
                data.sexe
            );

            fillField(
                "date_naissance",
                data.date_naissance
            );

            fillField(
                "email",
                data.email
            );

            fillField(
                "telephone",
                data.telephone
            );

            fillField(
                "organisation",
                data.organisation
            );

            fillField(
                "matricule",
                data.matricule
            );

            fillField(
                "departement",
                data.departement
            );

            fillField(
                "fonction",
                data.fonction
            );

            fillField(
                "site_affectation",
                data.site_affectation
            );

            fillField(
                "responsable",
                data.responsable
            );

            fillField(
                "motif",
                data.motif
            );


            assignedUsername.value =
                data.assigned_username
                ||
                "";


            assignedRole.value =
                data.role
                ||
                "OPERATOR";


            accessLevel.value =
                data.access_level
                ||
                "STANDARD";


            accountExpiry.value =
                data.account_expiry
                ||
                "";


            renderPhoto(
                data.photo
            );


            message.textContent =
                "";


            noSelection.classList.add(
                "hidden"
            );


            form.classList.remove(
                "hidden"
            );


            setEditMode(
                false
            );


            document
                .querySelectorAll(
                    ".request-card"
                )
                .forEach(
                    card => {

                        card.classList.toggle(

                            "selected",

                            card.dataset.id
                            ===
                            data.request_id

                        );

                    }
                );

        }


        function renderList(){

            list.innerHTML =
                "";


            const pending =
                requests.filter(
                    item =>
                        item.status
                        ===
                        "PENDING"
                );


            count.textContent =
                pending.length;


            if(
                requests.length === 0
            ){

                list.innerHTML =
                    '<div class="empty-message">'
                    +
                    'Aucune demande.'
                    +
                    '</div>';

                return;

            }


            requests.forEach(
                request => {

                    const card =
                        document.createElement(
                            "div"
                        );


                    card.className =
                        "request-card";


                    card.dataset.id =
                        request.request_id;


                    card.innerHTML = `

                        <div class="request-card-name">

                            ${request.nom || ""}
                            ${request.postnom || ""}
                            ${request.prenom || ""}

                        </div>

                        <div class="request-card-email">

                            ${request.email || ""}

                        </div>

                        <div class="request-card-bottom">

                            <span class="request-card-id">

                                ${request.request_id}

                            </span>

                            <span class="request-card-status">

                                ${request.status}

                            </span>

                        </div>

                    `;


                    card.addEventListener(
                        "click",
                        () => {

                            selectRequest(
                                request
                            );

                        }
                    );


                    list.appendChild(
                        card
                    );

                }
            );

        }


        async function loadRequests(){

            try{

                const response =
                    await fetch(
                        "/api/admin/account-requests",
                        {
                            credentials:
                                "same-origin"
                        }
                    );


                if(!response.ok){

                    throw new Error(
                        "Chargement impossible"
                    );

                }


                requests =
                    await response.json();


                renderList();

            }

            catch(error){

                console.error(
                    error
                );


                list.innerHTML =
                    '<div class="empty-message">'
                    +
                    'Erreur de chargement.'
                    +
                    '</div>';

            }

        }


        photoInput.addEventListener(
            "change",
            () => {

                const file =
                    photoInput.files[0];


                if(!file){

                    return;

                }


                renderPhoto(
                    URL.createObjectURL(
                        file
                    )
                );

            }
        );


        editButton.addEventListener(
            "click",
            () => {

                setEditMode(
                    !editMode
                );

            }
        );


        copyCredentials.addEventListener(
            "click",
            async () => {

                const text =
                    "Identifiant : "
                    +
                    createdUsername.textContent
                    +
                    "\nMot de passe temporaire : "
                    +
                    temporaryPassword.textContent;


                try{

                    await navigator
                        .clipboard
                        .writeText(
                            text
                        );


                    copyCredentials.textContent =
                        "Copié";

                }

                catch(error){

                    console.error(
                        error
                    );

                }

            }
        );


        form.addEventListener(
            "submit",
            async event => {

                event.preventDefault();


                if(!selected){

                    return;

                }


                const username =
                    assignedUsername
                        .value
                        .trim()
                        .toLowerCase();


                const usernamePattern =
                    /^(?=.*[a-z])(?=.*\d)[a-z0-9]{5,20}$/;


                if(
                    !usernamePattern
                        .test(
                            username
                        )
                ){

                    message.style.color =
                        "#ff5267";


                    message.textContent =
                        "Identifiant invalide : 5 à 20 caractères avec au moins une lettre et un chiffre.";


                    return;

                }


                const data =
                    new FormData();


                data.append(
                    "assigned_username",
                    username
                );


                data.append(
                    "role",
                    assignedRole.value
                );


                data.append(
                    "access_level",
                    accessLevel.value
                );


                data.append(
                    "account_expiry",
                    accountExpiry.value
                );


                Object.entries(
                    fields
                ).forEach(
                    ([name, field]) => {

                        /*
                        Protection contre un élément HTML absent.
                        */

                        if(!field){

                            console.error(
                                "Champ Phoenix Admin introuvable :",
                                name
                            );

                            return;

                        }

                        data.append(
                            name,
                            field.value.trim()
                        );

                    }
                );


                const photo =
                    photoInput.files[0];


                if(photo){

                    data.append(
                        "photo",
                        photo
                    );

                }


                saveButton.disabled =
                    true;


                saveButton.textContent =
                    "Enregistrement...";


                credentialsBox.classList.add(
                    "hidden"
                );


                try{

                    const response =
                        await fetch(

                            "/api/admin/account-requests/"
                            +
                            encodeURIComponent(
                                selected.request_id
                            ),

                            {

                                method:"POST",

                                credentials:
                                    "same-origin",

                                body:data

                            }

                        );


                    const result =
                        await response.json();


                    if(
                        !response.ok
                        ||
                        !result.success
                    ){

                        message.style.color =
                            "#ff5267";


                        message.textContent =
                            result.message
                            ||
                            "Enregistrement impossible.";


                        return;

                    }


                    message.style.color =
                        "#19bf72";


                    if(
                        result.account_created
                        &&
                        result.temporary_password
                    ){

                    if(result.email_sent){

                        message.textContent =
                            "Compte créé avec succès. L'e-mail d'activation a été envoyé.";

                    }

                    else if(
                        result.email_status
                        ===
                        "SMTP_NOT_CONFIGURED"
                    ){

                        message.textContent =
                            "Compte créé avec succès. Le service e-mail Phoenix n'est pas encore configuré.";

                    }

                    else{

                        message.textContent =
                            "Compte créé avec succès, mais l'e-mail d'activation n'a pas pu être envoyé.";

                    }


                        createdUsername.textContent =
                            result.username;


                        temporaryPassword.textContent =
                            result.temporary_password;


                        credentialsBox.classList.remove(
                            "hidden"
                        );

                    }

                    else{

                        message.textContent =
                            "Informations enregistrées avec succès.";

                    }


                    photoInput.value =
                        "";


                    await loadRequests();


                    const updated =
                        requests.find(
                            item =>
                                item.request_id
                                ===
                                selected.request_id
                        );


                    if(updated){

                        /*
                        Ne pas appeler selectRequest immédiatement
                        lorsqu'un mot de passe vient d'être créé,
                        sinon la boîte disparaîtrait.
                        */

                        selected = updated;

                    }

                }

                catch(error){

                    console.error(
                        error
                    );


                    message.style.color =
                        "#ff5267";


                    message.textContent =
                        "Phoenix Server ne répond pas.";

                }

                finally{

                    saveButton.disabled =
                        false;


                    saveButton.textContent =
                        "Enregistrer";

                }

            }
        );


        loadRequests();

    }
);