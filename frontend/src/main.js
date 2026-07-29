document.getElementById("root").innerHTML = `
<div style="
  min-height:100vh;
  background:#0f172a;
  color:white;
  padding:50px;
  font-family:Arial;
  text-align:center;
">

<h1>Ultimate AI Translator</h1>

<p>Select your SRT subtitle file</p>

<div style="
  margin:40px auto;
  max-width:500px;
  padding:30px;
  background:#1e293b;
  border-radius:20px;
">

<h2>Upload SRT File</h2>

<input
  id="fileInput"
  type="file"
  accept=".srt"
/>

<p id="fileName">
No file selected
</p>

<br>

<button id="translateBtn">
Start Translation
</button>

</div>

</div>
`;

const fileInput =
document.getElementById("fileInput");

const fileName =
document.getElementById("fileName");

fileInput.addEventListener(
"change",
function(){

if(fileInput.files.length>0){

fileName.textContent =
fileInput.files[0].name;

}else{

fileName.textContent =
"No file selected";

}

});
import { uploadSrt } from "./api.js";

const translateBtn =
document.getElementById("translateBtn");

translateBtn.addEventListener(
"click",
async function(){

if(fileInput.files.length===0){

alert(
"Please select an SRT file."
);

return;

}

translateBtn.disabled=true;
translateBtn.textContent="Uploading...";

try{

const result=
await uploadSrt(
fileInput.files[0]
);

console.log(result);

alert(
"Upload successful!\n\nJob ID: "+
result.job_id
);

}catch(error){

console.error(error);

alert(
"Upload failed."
);

}

translateBtn.disabled=false;
translateBtn.textContent=
"Start Translation";

});
