async function lookupPhone() {
  const phone = document.getElementById("phone").value;
  if (!phone) {
    alert("Please enter a phone number");
    return;
  }

  const response = await fetch("/lookup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ phone })
  });

  const data = await response.json();
  const resultDiv = document.getElementById("result");

  if (data.error) {
    resultDiv.innerHTML = `<p style="color:red;">Error: ${data.error}</p>`;
  } else {
    resultDiv.innerHTML = `
      <p><b>Country:</b> ${data.Country}</p>
      <p><b>Region/Area:</b> ${data["Region/Area"]}</p>
      <p><b>Carrier:</b> ${data.Carrier}</p>
      <p><b>Timezone:</b> ${data.Timezone}</p>
      <p><b>Formatted Number:</b> ${data["Formatted Number"]}</p>
      <p><b>Validity:</b> ${data.Validity ? "Valid" : "Invalid"}</p>
    `;
  }
}
