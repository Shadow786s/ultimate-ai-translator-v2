const API_BASE_URL =
"https://ultimate-ai-translator-v2.onrender.com";

export async function uploadSrt(file){

const formData = new FormData();

formData.append(
"file",
file
);

const response =
await fetch(
`${API_BASE_URL}/api/upload?batch_size=100`,
{
method:"POST",
body:formData
}
);

const data = await response.json();

if(!response.ok){

throw new Error(
data.detail || JSON.stringify(data)
);

}

return data;
}
