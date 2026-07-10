/* DOM Elements */
// Embed Builder
const createEmbedBtn = document.getElementById("create-embed-btn");
const editEmbedBtn = document.getElementById("edit-embed-btn");
const embedTextSend = document.getElementById("embed-text-send");
const colorPicker = document.getElementById("color-picker");
const colorVal = document.getElementById("color-value");
const resetColorBtn = document.getElementById("reset-color-btn");
const iconURLInput = document.getElementById("icon-url");
const iconNameInput = document.getElementById("icon-name");
const iconNameURLInput = document.getElementById("icon-name-url");
const titleInput = document.getElementById("title");
const titleURLInput = document.getElementById("title-url");
const embedTextInput = document.getElementById("embed-text");
const fieldsContainer = document.getElementById("fields-container");
const addFieldBtn = document.getElementById("add-field-btn");
const fieldCount = document.querySelector(".field-count");
const maxFieldsLength = fieldsContainer.getAttribute("max-fields") || 25;
const imageURLInput = document.getElementById("image-url");
const thumbnailURLInput = document.getElementById("thumbnail-url");
const footerInput = document.getElementById("footer");
const footerIconURLInput = document.getElementById("footer-icon-url");
const addEmbedBtn = document.getElementById("add-embed-btn");
const embedGuildSelect = document.getElementById("embed-guild-select");
const embedChannelSelect = document.getElementById("embed-channel-select");

// Embed Preview
const previewBG = document.querySelector(".preview-background");
const previewIcon = document.getElementById("preview-icon");
const previewIconName = document.getElementById("preview-icon-name");
const previewIconNameURL = document.getElementById("preview-icon-name-url");
const previewTitle = document.getElementById("preview-title");
const previewTitleURL = document.getElementById("preview-title-url");
const previewDesc = document.getElementById("preview-desc");
const previewThumbnail = document.getElementById("preview-thumbnail");
const previewFieldsContainer = document.querySelector(".preview-fields-container");
const previewImage = document.getElementById("preview-image");
const previewFooterIcon = document.getElementById("preview-footer-icon");
const previewFooter = document.getElementById("preview-footer");

/* DOM Content Loaded */
document.addEventListener("DOMContentLoaded", () => {
  loadGuilds();

  [embedTextSend, titleInput, embedTextInput, footerInput].forEach(input => wordCounter(input));
  fieldCount.textContent = `${fieldsContainer.children.length}/${maxFieldsLength} Fields`;

  syncText(iconNameInput, previewIconName);
  syncText(titleInput, previewTitle);
  syncText(embedTextInput, previewDesc);
  syncText(footerInput, previewFooter);

  syncTextURL(iconNameURLInput, previewIconNameURL);
  syncTextURL(titleURLInput, previewTitleURL);

  syncImage(imageURLInput, previewImage);
  syncImage(thumbnailURLInput, previewThumbnail);
  syncImage(iconURLInput, previewIcon);
  syncImage(footerIconURLInput, previewFooterIcon);
});

/* Main Functions */
// Embed Builder
async function loadGuilds(){
  try{
    embedGuildSelect.innerHTML = `
      <option value="" disabled selected>Loading guilds...</option>
    `;

    const response = await fetch(`${BACKEND_URL}/api/guilds`);
    if (!response.ok) throw new Error("Could not load guilds.");
    const guilds = await response.json();

    if (guilds.length === 0){
      embedGuildSelect.innerHTML = `
        <option value="" disabled selected>No guilds found</option>
      `;
      return;
    }

    embedGuildSelect.innerHTML = `
      <option value="" disabled selected>Choose a server...</option>
    `;

    guilds.forEach(guild => {
      const option = document.createElement("option");
      option.value = guild.id;
      option.textContent = guild.name;
      embedGuildSelect.appendChild(option);
    });

  } catch (err){
    console.error("Failed to load guilds: ", err);
    embedGuildSelect.innerHTML = `
      <option value="" disabled>Error loading guilds</option>
    `;
  }
}

embedGuildSelect.addEventListener("change", () => {
  loadChannels(embedGuildSelect.value);
});

async function loadChannels(guildId){
  try{
    embedChannelSelect.disabled = true;
    embedChannelSelect.innerHTML = `
      <option value="" disabled selected>Loading channels...</option>
    `;

    const response = await fetch(`${BACKEND_URL}/api/channels/${guildId}`);
    if (!response.ok) throw new Error("Could not load channels.");
    const channels = await response.json();

    if (channels.length === 0){
      embedChannelSelect.innerHTML = `
        <option value="" disabled>No text channels found</option>
      `;
      return;
    }

    embedChannelSelect.innerHTML = `
      <option value="" disabled selected>Choose a channel...</option>
    `;

    channels.forEach(channel => {
      const option = document.createElement("option");
      option.value = channel.id;
      option.textContent = "#" + channel.name;
      embedChannelSelect.appendChild(option);
    });

    embedChannelSelect.disabled = false;
    
  } catch (err){
    console.error("Failed to load channels:", err);
    embedChannelSelect.innerHTML = `
      <option value="" disabled>Error loading channels</option>
    `;
  }
}

colorPicker.addEventListener("input", () => {
  colorVal.textContent = `${colorPicker.value.toUpperCase()}`;
  previewBG.style.backgroundColor = colorPicker.value;
});

resetColorBtn.addEventListener("click", () => {
  colorPicker.value = "#5865f2";
  colorVal.textContent = "#5865f2";
  previewBG.style.backgroundColor = "#5865f2";
})

function wordCounter(inputElement){
  const wordCountElement = inputElement.parentElement.querySelector(".word-count");
  if (!wordCountElement) return;

  const currentWordCount = wordCountElement.querySelector("#current");
  const maxWordCount = wordCountElement.querySelector("#max");
  const maxLength = inputElement.getAttribute("maxlength");

  function updateCount(){
    currentWordCount.textContent = inputElement.value.length;
    maxWordCount.textContent = maxLength;
  }

  updateCount();
  inputElement.addEventListener("input", updateCount);
}

addFieldBtn.addEventListener("click", addField);

function addField(){
  if (fieldsContainer.children.length >= maxFieldsLength){
    return;
  }

  if (fieldsContainer.children.length + 1 == maxFieldsLength){
    addFieldBtn.textContent = "Maximum amount of fields reached!"
  }

  const field = document.createElement("div");
  field.className = "field";
  field.innerHTML = `
    <div class="word-count-container field-title-area">
      <input type="text" class="field-title" maxlength="300" placeholder="Title for field ${fieldsContainer.children.length + 1}">
      <h5 class="word-count"><span id="current">0</span>/<span id="max">300</span></h5>
    </div>
    <div class="inline-container">
      <label for="inline-checkbox">Inline: </label>
      <input type="checkbox" class="inline-checkbox">
    </div>
    <button type="button" class="remove-field-btn">X</button>
    <div class="word-count-container field-desc-area">
      <input type="text" class="field-desc" maxlength="1000" placeholder="Description">
      <h5 class="word-count"><span id="current">0</span>/<span id="max">1000</span></h5>
    </div>
  `;

  fieldsContainer.appendChild(field);
  fieldCount.textContent = `${fieldsContainer.children.length}/${maxFieldsLength} Fields`;

  initialiseField(field);
}

function initialiseField(field){
  const fieldTitleInput = field.querySelector(".field-title");
  const fieldDescInput = field.querySelector(".field-desc");
  const inlineCheckbox = field.querySelector(".inline-checkbox");
  const removeFieldBtn = field.querySelector(".remove-field-btn");

  [fieldTitleInput, fieldDescInput].forEach(wordCounter);

  [fieldTitleInput, fieldDescInput].forEach(element => {
    element.addEventListener("input", updatePreviewField);
  });

  inlineCheckbox.addEventListener("change", updatePreviewField);

  removeFieldBtn.addEventListener("click", () => {
    field.remove();
    addFieldBtn.textContent = "Add Field";
    fieldCount.textContent = `${fieldsContainer.children.length}/${maxFieldsLength} Fields`;
    
    const fields = fieldsContainer.querySelectorAll(".field");
    fields.forEach((currentField, index) => {
      const titleInput = currentField.querySelector(".field-title");
      if (titleInput){
        titleInput.placeholder = `Title for field ${index + 1}`;
      }
    });

    updatePreviewField();
  });
}

addEmbedBtn.addEventListener("click", addEmbed);

async function addEmbed(){
  if (!embedChannelSelect.value){
    alert("Please select a channel first!");
    return;
  }

  /* INFO */
  // Fields
  const fieldsList = [];
  const fields = fieldsContainer.querySelectorAll(".field");

  fields.forEach(field => {
    const fieldTitleInput = field.querySelector(".field-title");
    const fieldDescInput = field.querySelector(".field-desc");
    const fieldInlineCheckbox = field.querySelector(".inline-checkbox");

    const fieldTitleVal = fieldTitleInput ? fieldTitleInput.value.trim() : "";
    const fieldDescVal = fieldDescInput ? fieldDescInput.value.trim() : "";
    const isInline = fieldInlineCheckbox ? fieldInlineCheckbox.checked : false;

    if (fieldTitleVal !== "" || fieldDescVal !== ""){
      fieldsList.push({
        title: fieldTitleVal || "Field Title",
        desc: fieldDescVal || "Field Description",
        inline: isInline
      });
    }
  })

  // Check Blank
  const isFormCompletelyBlank = 
    !embedTextSend.value.trim() &&
    !titleInput.value.trim() &&
    !titleURLInput.value.trim() &&
    !embedTextInput.value.trim() &&
    !iconURLInput.value.trim() &&
    !iconNameInput.value.trim() &&
    !iconNameURLInput.value.trim() &&
    !imageURLInput.value.trim() &&
    !thumbnailURLInput.value.trim() &&
    !footerInput.value.trim() &&
    !footerIconURLInput.value.trim() &&
    fieldsList.length === 0;

  if (isFormCompletelyBlank){
    alert("You cannot send an empty embed! Please fill out at least one field.");
    return;
  }

  // Send Info
  const info = {
    channel_id: embedChannelSelect.value,
    embed_text_send: embedTextSend.value || null,
    color: colorPicker.value || "#5865f2",
    title: titleInput.value || null,
    title_url: titleURLInput.value || null,
    description: embedTextInput.value || null,
    author: {
      icon_url: iconURLInput.value || null,
      icon_name: iconNameInput.value || null,
      icon_name_url: iconNameURLInput.value || null
    },
    fields: fieldsList,
    image_url: imageURLInput.value || null,
    thumbnail_url: thumbnailURLInput.value || null,
    footer: footerInput.value || null,
    footer_icon_url: footerIconURLInput.value || null
  }

  /* SENDING */
  addEmbedBtn.textContent = "Sending...";
  addEmbedBtn.disabled = true;

  try{
    const response = await fetch(`${BACKEND_URL}/api/send_embed`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(info)
    });
    const data = await response.json();

    if (response.ok){
      alert(`Embed successfully sent to ${embedChannelSelect.options[embedChannelSelect.selectedIndex].textContent}!`);
      
      /* Reset Input */
      // Embed Builder
      embedTextSend.value = "";
      colorPicker.value = "#5865f2";
      titleInput.value = "";
      titleURLInput.value = "";
      embedTextInput.value = "";
      iconURLInput.value = "";
      iconNameInput.value = "";
      iconNameURLInput.value = "";
      imageURLInput.value = "";
      thumbnailURLInput.value = "";
      footerInput.value = "";
      footerIconURLInput.value = "";
      fieldsContainer.innerHTML = "";
      fieldCount.textContent = `0/${maxFieldsLength} Fields`;
      [embedTextSend, titleInput, embedTextInput, footerInput].forEach(input => {
        input.value = ""
        const container = input.closest(".word-count-container");
        if (container){
          const counterSpan = container.querySelector("#current");
          if (counterSpan){
            counterSpan.textContent = "0";
          }
        }
      });
      
      // Embed Preview
      previewBG.style.backgroundColor = "#5865f2";

      [previewIconName, previewTitle, previewDesc, previewFooter].forEach(input => {
        input.style.display = "none";
        input.textContent = "";
      });

      [previewIconNameURL, previewTitleURL].forEach(input => {
        input.href = "#";
        input.style.color = "#fff";
        input.classList.add("disabled-link");
      });

      [previewImage, previewThumbnail, previewIcon, previewFooterIcon].forEach(input => {
        input.style.display = "none";
        input.src = "";
      });

      previewFieldsContainer.innerHTML = "";

    } else{
      alert(`Failed to send embed: ${data.error}`);
    }

  } catch (err){
    console.error("Failed to add embed:", err);

  } finally{
    addEmbedBtn.innerText = "Add Embed";
    addEmbedBtn.disabled = false;
  }
}

// Embed Preview
function syncText(inputElement, previewElement){
  if (!inputElement || !previewElement) return;
  previewElement.textContent = "";

  inputElement.addEventListener("input", () => {
    const value = inputElement.value.trim();
    previewElement.textContent = value;

    if (value === ""){
      previewElement.style.display = fallbackText ? "block" : "none";
    } else {
      previewElement.style.display = "block";
    }
  });
}

function syncTextURL(inputElement, previewElement){
  if (!inputElement || !previewElement) return;
  previewElement.href = "#";

  inputElement.addEventListener("input", () => {
    const value = inputElement.value.trim();
    previewElement.href = value;

    if (value === ""){
      previewElement.style.color = "#fff";
      previewElement.classList.add("disabled-link");
    } else {
      if (previewElement === previewIconNameURL) previewElement.style.color = "#fff";
      else if (previewElement === previewTitleURL) previewElement.style.color = "#4D96EE";
      previewElement.classList.remove("disabled-link");
    }
  });
}

function syncImage(inputElement, imgElement){
  if (!inputElement || !imgElement) return;
  imgElement.src = "";

  inputElement.addEventListener("input", () => {
    const url = inputElement.value.trim();
    if (url){
      imgElement.src = url;
      imgElement.style.display = "block";
    } else {
      imgElement.style.display = "none";
    }
  });
}

function updatePreviewField(){
  previewFieldsContainer.innerHTML = "";

  const fields = fieldsContainer.querySelectorAll(".field");
  fields.forEach(field => {
    const fieldTitleEl = field.querySelector(".field-title");
    const fieldDescEl = field.querySelector(".field-desc");
    const inlineCheckbox = field.querySelector(".inline-checkbox");

    if (!fieldTitleEl || !fieldDescEl) return;

    const fieldTitleVal = fieldTitleEl.value.trim();
    const fieldDescVal = fieldDescEl.value.trim();
    const isInline = inlineCheckbox ? inlineCheckbox.checked : false;

    if (fieldTitleVal || fieldDescVal){
      const previewField = document.createElement("div");
      previewField.classList.add("preview-field");
      if (isInline) previewField.classList.add("inline");

      const previewFieldTitle = document.createElement("span");
      previewFieldTitle.classList.add("preview-field-title");
      previewFieldTitle.textContent = fieldTitleVal;
      previewFieldTitle.style.display = "block";

      const previewFieldDesc = document.createElement("span");
      previewFieldDesc.classList.add("preview-field-desc");
      previewFieldDesc.textContent = fieldDescVal;
      previewFieldDesc.style.display = "block";

      previewField.appendChild(previewFieldTitle);
      previewField.appendChild(previewFieldDesc);

      previewFieldsContainer.appendChild(previewField);
    }
  });
}