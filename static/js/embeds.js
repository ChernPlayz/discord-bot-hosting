/* DOM Elements */
// Embed Builder
const createEmbedBtn = document.getElementById("create-embed-btn");
const editEmbedBtn = document.getElementById("edit-embed-btn");
const embedTextSend = document.getElementById("embed-text-send");
const colorPicker = document.getElementById("color-picker");
const colorVal = document.getElementById("color-value");
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

/* DOM Content Loaded */
document.addEventListener("DOMContentLoaded", () => {
  loadGuilds();
  fieldCount.textContent = `${fieldsContainer.children.length}/${maxFieldsLength} Fields`;
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
  colorVal.textContent = `#${colorPicker.value.toUpperCase()}`;
});

function wordCounter(inputElement){
  const wordCountElement = inputElement.parentElement.querySelector(".word-count");
  if (!wordCountElement) return;

  const currentWordCount = wordCountElement.querySelector("#current");
  const maxWordCount = wordCountElement.querySelector("#max");

  inputElement.addEventListener("input", () => {
    const maxLength = inputElement.getAttribute("maxlength") || 2000;
    currentWordCount.textContent = inputElement.value.length;
    maxWordCount.textContent = maxLength;
  });
}
[embedTextSend, titleInput, embedTextInput, footerInput].forEach(wordCounter);

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
  const removeFieldBtn = field.querySelector(".remove-field-btn");

  [fieldTitleInput, fieldDescInput].forEach(wordCounter);

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
  });
}

addEmbedBtn.addEventListener("click", addEmbed);

async function addEmbed(){
  if (!embedChannelSelect.value){
    alert("Please select a destination channel first!");
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
        desc: fieldDescVal || "Field Content",
        inline: isInline
      });
    }
  })

  // Others
  const info = {
    channel_id: embedChannelSelect.value,
    content: embedTextSend.value || null,
    color: colorPicker.value || "#5865f2",
    title: titleInput.value || null,
    title_url: titleURLInput.value || null,
    description: embedTextInput.value || null,
    author: {
      name: iconNameInput.value || null,
      url: iconNameURLInput.value || null,
      icon_url: iconURLInput.value || null
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
      body: JSON.stringify(payload)
    });

    const data = await response.json();

    if (response.ok){
      alert(`Embed successfully sent to ${embedChannelSelect.options[embedChannelSelect.selectedIndex].textContent}!`);
    } else{
      alert(`Error: ${data.detail || "Failed to send embed."}`);
    }

  } catch (err){
    console.error("Network error:", err);
    alert("Could not reach your bot. Check if Render instance is active/awake.");

  } finally{
    addEmbedBtn.innerText = "Add Embed";
    addEmbedBtn.disabled = false;
  }
}