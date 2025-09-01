async function getInfo() {
  const number = document.getElementById("phoneInput").value;
  const resultBox = document.getElementById("result");
  resultBox.textContent = "Fetching details...";

  try {
    const response = await fetch("/get_info", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ number })
    });

    const data = await response.json();
    resultBox.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    resultBox.textContent = "Error fetching details: " + error;
  }
}
