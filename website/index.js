const colorPicker = document.querySelector("input");
const colorOutput = document.querySelector("label");

addEventListener("input", (event) => {
  colorOutput.innerText = colorPicker.value;
});