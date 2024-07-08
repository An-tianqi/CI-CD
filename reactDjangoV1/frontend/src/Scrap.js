import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axiosInstance from "./axiosConfig";
import "./Scrap.css";

const Scrap = ({ updateTickets }) => {
  const [brandBasique, setBrandBasique] = useState("");
  const [cityBasique, setCityBasique] = useState("");
  const [brandMedium, setBrandMedium] = useState("");
  const [cityMedium, setCityMedium] = useState("");
  const [brandPremium, setBrandPremium] = useState("");
  const [cityPremium, setCityPremium] = useState("");
  const [loading, setLoading] = useState(false);
  const [scrapType, setScrapType] = useState("");
  const [selectedPackage, setSelectedPackage] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = () => {
    let brand, city;

    switch (scrapType) {
      case "medium":
        brand = brandMedium;
        city = cityMedium;
        break;
      case "premium":
        brand = brandPremium;
        city = cityPremium;
        break;
      default:
        brand = brandBasique;
        city = cityBasique;
    }

    if (!brand || !city) {
      alert("Tous les champs doivent être remplis.");
      return;
    }
    setLoading(true);
    let apiRoute = "";
    switch (scrapType) {
      case "medium":
        apiRoute = "/api/submit_form_medium";
        break;
      case "premium":
        apiRoute = "/api/submit_form_prenium";
        break;
      default:
        apiRoute = "/api/submit_form_basique";
    }

    axiosInstance
      .post(
        apiRoute,
        { brand, city },
        {
          headers: {
            Authorization: `Token ${localStorage.getItem("token")}`,
            "Content-Type": "application/json",
          },
          responseType: "blob", // Important: indiquez à axios de traiter la réponse comme un blob
        }
      )
      .then((response) => {
        if (response.status === 200) {
          if (response.data.message === undefined) {
            alert("Scraping réussi et résultats envoyés par email!");
          } else {
            alert(response.data.message);
          }
          // Mettre à jour les tickets après le scraping
          axiosInstance
            .get("/api/user/", {
              headers: {
                Authorization: `Token ${localStorage.getItem("token")}`,
              },
            })
            .then((response) => {
              updateTickets(response.data.tickets);
            })
            .catch((error) => {
              console.error("Error fetching user:", error);
            });
          // Vider le formulaire après le succès
          setBrandBasique("");
          setCityBasique("");
          setBrandMedium("");
          setCityMedium("");
          setBrandPremium("");
          setCityPremium("");
          setScrapType("");
          setSelectedPackage(null);
        } else {
          alert(
            "Erreur: la réponse du serveur n'est pas conforme aux attentes."
          );
        }
        setLoading(false);
      })
      .catch(async (error) => {
        if (
          error.response &&
          error.response.data &&
          error.response.data.type === "application/json"
        ) {
          const text = await error.response.data.text();
          const errorMessage = JSON.parse(text).message;
          if (window.confirm(`${errorMessage}`)) {
            navigate("/shop");
          } else {
            navigate("/scrap");
          }
        } else {
          alert("Une erreur est survenue lors de la soumission.");
        }
        setLoading(false);
      });
  };

  const handleViewMore = (index) => {
    setSelectedPackage(selectedPackage === index ? null : index);
    setScrapType(packages[index].type);
  };

  const packages = [
    {
      title: "Scrap Basique",
      subtitle: "Basic scrapping options",
      price: "Free",
      description:
        "Basic scrapping with limited features. Suitable for small tasks.",
      details:
        "Includes basic scrapping features with limited usage. Great for small tasks and personal use.",
      type: "basique",
    },
    {
      title: "Scrap Medium",
      subtitle: "Standard scrapping options",
      price: "2 tickets/scrap",
      description: "Standard scrapping with more features and higher limits.",
      details:
        "Includes standard scrapping features with higher usage limits. Ideal for moderate tasks and small businesses.",
      type: "medium",
    },
    {
      title: "Scrap Premium",
      subtitle: "Premium scrapping options",
      price: "3 tickets/scrap",
      description: "Premium scrapping with all features and highest limits.",
      details:
        "Includes all scrapping features with the highest usage limits. Perfect for large tasks and enterprises.",
      type: "premium",
    },
  ];

  const handleBackgroundClick = (e) => {
    if (e.target.className === "scrap-page") {
      setSelectedPackage(null);
    }
  };

  return (
    <div className="scrap-page" onClick={handleBackgroundClick}>
      <h1 className="scrap-title">Scrapping Packages</h1>
      <div className="packages">
        {packages.map((pkg, index) => (
          <div
            key={index}
            className={`package-card ${
              selectedPackage === index
                ? "selected"
                : selectedPackage !== null
                ? "blurred"
                : ""
            }`}
            style={{
              transform: selectedPackage === index ? "scale(1.2)" : "scale(1)",
            }}
            onClick={() => handleViewMore(index)}
          >
            <h2>{pkg.title}</h2>
            <h3>{pkg.subtitle}</h3>
            <p className="price">{pkg.price}</p>
            <p>{pkg.description}</p>
            {selectedPackage === index && (
              <>
                <p className="details">{pkg.details}</p>
                <div className="form-box" onClick={(e) => e.stopPropagation()}>
                  <input
                    type="text"
                    value={
                      scrapType === "basique"
                        ? brandBasique
                        : scrapType === "medium"
                        ? brandMedium
                        : brandPremium
                    }
                    onChange={(e) => {
                      const value = e.target.value;
                      if (scrapType === "basique") setBrandBasique(value);
                      else if (scrapType === "medium") setBrandMedium(value);
                      else setBrandPremium(value);
                    }}
                    placeholder="Enseigne à scraper"
                  />
                  <input
                    type="text"
                    value={
                      scrapType === "basique"
                        ? cityBasique
                        : scrapType === "medium"
                        ? cityMedium
                        : cityPremium
                    }
                    onChange={(e) => {
                      const value = e.target.value;
                      if (scrapType === "basique") setCityBasique(value);
                      else if (scrapType === "medium") setCityMedium(value);
                      else setCityPremium(value);
                    }}
                    placeholder="Nom de la Ville"
                  />
                  <button onClick={handleSubmit} disabled={loading}>
                    Submit
                  </button>
                  {loading && (
                    <img
                      src="/images/ninja.gif"
                      alt="Loading..."
                      className="loading-gif"
                    />
                  )}
                </div>
              </>
            )}
            <button onClick={() => handleViewMore(index)}>
              {selectedPackage === index ? "View less" : "Start Scrapping"}
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Scrap;
