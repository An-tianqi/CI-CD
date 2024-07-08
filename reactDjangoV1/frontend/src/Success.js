import React, { useEffect, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import axiosInstance from "./axiosConfig";

const Success = ({ updateTickets }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const hasCalledAPI = useRef(false); // Ajoutez un drapeau pour suivre si l'appel API a été effectué

  useEffect(() => {
    debugger;
    const query = new URLSearchParams(location.search);
    const sessionId = query.get("session_id");

    if (sessionId && !hasCalledAPI.current) {
      hasCalledAPI.current = true; // Définissez le drapeau sur true pour éviter les appels répétés
      axiosInstance
        .post(
          "/api/buy_tickets",
          { session_id: sessionId },
          {
            headers: {
              Authorization: `Token ${localStorage.getItem("token")}`,
            },
          }
        )
        .then((response) => {
          debugger;
          alert("Tickets purchased successfully");
          updateTickets(response.data.tickets);
          navigate("/scrap"); // Redirect to scrap page
        })
        .catch((error) => {
          debugger;
          alert(
            "Purchase failed: " +
              (error.response ? error.response.data.message : error.message)
          );
          navigate("/shop"); // Redirect back to shop page
        });
    }
  }, [location.search, navigate, updateTickets]);

  return (
    <div>
      <h1>Processing your payment...</h1>
    </div>
  );
};

export default Success;