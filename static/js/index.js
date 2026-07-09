/* DOM Elements */
const userIcon = document.getElementById("userIcon");
const username = document.getElementById("username");
const toggleModeBtn = document.getElementById("toggleModeBtn");
const toggleSidebarBtn = document.getElementById("toggleSidebarBtn");
const sidebar = document.getElementById("sidebar");
const liBtns = document.querySelectorAll(".li-btn")
const html = document.documentElement;

/* URL & API */
const BACKEND_URL = "https://discord-bot-hosting-vft8.onrender.com/";

/* DOM Content Loaded */
document.addEventListener("DOMContentLoaded", () => {
  const currentTheme = localStorage.getItem("theme") || "light";
  html.setAttribute("data-theme", currentTheme);
  toggleModeBtn.innerHTML = currentTheme === "light" ? `
  <svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 -960 960 960" width="20px" fill="#e3e3e3"><path d="M479.96-144Q340-144 242-242t-98-238q0-140 97.93-238t237.83-98q13.06 0 25.65 1 12.59 1 25.59 3-39 29-62 72t-23 92q0 85 58.5 143.5T648-446q49 0 92-23t72-62q2 13 3 25.59t1 25.65q0 139.9-98.04 237.83t-238 97.93Z"/></svg>
  <span>Dark</span>
  `
  : `
  <svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 -960 960 960" width="20px" fill="#e3e3e3"><path d="M565-395q35-35 35-85t-35-85q-35-35-85-35t-85 35q-35 35-35 85t35 85q35 35 85 35t85-35Zm-221 51q-56-56-56-136t56-136q56-56 136-56t136 56q56 56 56 136t-56 136q-56 56-136 56t-136-56ZM216-444H48v-72h168v72Zm696 0H744v-72h168v72ZM444-744v-168h72v168h-72Zm0 696v-168h72v168h-72ZM269-642 166-742l51-55 102 104-50 51Zm474 475L642-268l49-51 103 101-51 51ZM640-691l102-101 51 49-100 103-53-51ZM163-217l105-99 49 47-98 104-56-52Zm317-263Z"/></svg>
  <span>Light</span>
  `;

  loadUserInfo();
});

/* Main Functions */
function toggleTheme(){
  const currentTheme = html.getAttribute("data-theme");
  const newTheme = currentTheme === "light" ? "dark" : "light";
  toggleModeBtn.innerHTML = newTheme === "light" ? `
  <svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 -960 960 960" width="20px" fill="#e3e3e3"><path d="M479.96-144Q340-144 242-242t-98-238q0-140 97.93-238t237.83-98q13.06 0 25.65 1 12.59 1 25.59 3-39 29-62 72t-23 92q0 85 58.5 143.5T648-446q49 0 92-23t72-62q2 13 3 25.59t1 25.65q0 139.9-98.04 237.83t-238 97.93Z"/></svg>
  <span>Dark</span>
  `
  : `
  <svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 -960 960 960" width="20px" fill="#e3e3e3"><path d="M565-395q35-35 35-85t-35-85q-35-35-85-35t-85 35q-35 35-35 85t35 85q35 35 85 35t85-35Zm-221 51q-56-56-56-136t56-136q56-56 136-56t136 56q56 56 56 136t-56 136q-56 56-136 56t-136-56ZM216-444H48v-72h168v72Zm696 0H744v-72h168v72ZM444-744v-168h72v168h-72Zm0 696v-168h72v168h-72ZM269-642 166-742l51-55 102 104-50 51Zm474 475L642-268l49-51 103 101-51 51ZM640-691l102-101 51 49-100 103-53-51ZM163-217l105-99 49 47-98 104-56-52Zm317-263Z"/></svg>
  <span>Light</span>
  `;
  html.setAttribute("data-theme", newTheme);
  localStorage.setItem("theme", newTheme);
}

function toggleSidebar(){
  sidebar.classList.toggle("close");
  toggleSidebarBtn.classList.toggle("rotate");
  closeAllSubMenus();
}

function toggleSubMenu(btn){
  const subMenu = btn.nextElementSibling;

  if (!subMenu.classList.contains("show")){
    closeAllSubMenus();
  }

  subMenu.classList.toggle("show");
  btn.classList.toggle("rotate");

  if (sidebar.classList.contains("close")){
    sidebar.classList.toggle("close");
    toggleSidebarBtn.classList.toggle("rotate");
  }
}

function closeAllSubMenus(){
  Array.from(sidebar.getElementsByClassName("show")).forEach(ul => {
    const dropdownBtn = ul.previousElementSibling;
    ul.classList.remove("show");
    dropdownBtn.classList.remove("rotate");
  })
}

liBtns.forEach(liBtn => {
  liBtn.addEventListener("click", () => {
    const currentActive = document.querySelector(".li-btn.active");
    if (currentActive){
      currentActive.classList.remove("active");
    }
    liBtn.classList.add("active");
    
    if (this.parentElement.parentElement.classList.contains("sub-menu")){
      this.parentElement.parentElement.classList.add("show");
      this.parentElement.parentElement.previousElementSibling.classList.add("rotate");
    }
  })
});

async function loadUserInfo(){
  try{
    const response = await fetch(`${BACKEND_URL}/api/user_data`);
    if (!response.ok) throw new Error("User unauthorized or API failed");
    const userData = await response.json();
    
    userIcon.src = userData.avatar_url;
    username.textContent = `Welcome, ${userData.username}!`;

  } catch (err){
    console.error("Failed to load user info: ", err);
  }
}