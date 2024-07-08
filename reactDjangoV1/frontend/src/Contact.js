import React, { useState } from "react";
import axiosInstance from "./axiosConfig";
import "./Contact.css";
import contactImage from "./image.png"; // Import the image

const Contact = () => {
  const [name, setName] = useState("");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axiosInstance.post(
        "/api/contact/",
        {
          name,
          subject,
          message,
        },
        {
          headers: {
            Authorization: `Token ${localStorage.getItem("token")}`,
            "Content-Type": "application/json",
          },
        }
      );
      alert(response.data.message);
      setName("");
      setSubject("");
      setMessage("");
    } catch (error) {
      alert(
        error.response && error.response.data && error.response.data.message
          ? error.response.data.message
          : "Une erreur s'est produite lors de l'envoi de votre message."
      );
    }
  };

  return (
    <div className="contact-page">
      <div className="contact-left">
        <img src={contactImage} alt="Contact" />
      </div>
      <div className="contact-right">
        <h1>Contactez-Nous</h1>
        <p>
          Si vous avez des questions, n'hésitez pas à nous contacter via email à
          info@scrap4you.com ou depuis ce formulaire.
        </p>
        <form className="contact-form" onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <input
            type="text"
            placeholder="Subject"
            value={subject}
            onChange={(e) => setSubject(e.target.value)}
          />
          <textarea
            placeholder="Message"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            style={{
              resize: "none",
            }}
          ></textarea>
          <button type="submit">Send</button>
        </form>
      </div>
    </div>
  );
};

export default Contact;
