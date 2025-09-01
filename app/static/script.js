async function lookupPhone() {
  const phone = document.getElementById("phone").value.trim();
  const resultDiv = document.getElementById("result");

  resultDiv.innerHTML = "<p>Fetching details...</p>";

  try {
    const response = await fetch("https://phone-number-location-finder.onrender.com/api/phone", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ phone }),
    });

    const data = await response.json();

    if (data.error) {
      resultDiv.innerHTML = `<p class="error"><b>Error:</b> ${data.error}</p>`;
      return;
    }

    resultDiv.innerHTML = `
      <p><b>Country:</b> ${data.country || '-'}</p>
      <p><b>Region/Area:</b> ${data.region || '-'}</p>
      <p><b>Carrier:</b> ${data.carrier || '-'}</p>
      <p><b>Line Type:</b> ${data.line_type || '-'}</p>
      <p><b>Timezone:</b> ${data.timezone || '-'}</p>
      <p><b>Formatted Number:</b> ${data.formatted_number || '-'}</p>
      <p><b>Country Code:</b> ${data.country_code || '-'}</p>
      <p><b>Validity:</b> ${data.validity || '-'}</p>
    `;
  } catch (err) {
    resultDiv.innerHTML = `<p class="error"><b>Failed to fetch data.</b></p>`;
  }
}
