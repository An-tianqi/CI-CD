import React from "react";
import axiosInstance from "./axiosConfig";
import { loadStripe } from "@stripe/stripe-js";
import './Shop.css';

const stripePromise = loadStripe(
  "pk_test_51LPtT9LIqjQ7Sl29dC93bDHkuaBVwN73rmQNeJPyQL2vnRAZ1TjYk9y4L8w9RmEV50mYKDUbDx0KLXWZRODi2XMg00Kg8uq8on"
);

const Shop = ({ updateTickets }) => {
  const handleBuyTickets = async (tickets) => {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("You need to log in first");
      return;
    }

    try {
      const response = await axiosInstance.post(
        "/api/create_checkout_session",
        { tickets: parseInt(tickets, 10) },
        {
          headers: {
            Authorization: `Token ${token}`,
          },
        }
      );

      const sessionId = response.data.sessionId;
      const stripe = await stripePromise;
      const { error } = await stripe.redirectToCheckout({ sessionId });
      if (error) {
        console.error("Stripe Checkout Error: ", error);
        alert("Achat échoué : " + error.message);
      }
    } catch (error) {
      alert(
        "Achat échoué: " +
          (error.response ? error.response.data.message : error.message)
      );
    }
  };

  return (
    <div className="shop-container">
      <div className="shop-header">
        <h1>Get Your Tickets</h1>
        <p>Choose the best plan for your scraping needs and enjoy exclusive features.</p>
      </div>
      <div className="shop-cards">
        <div className="shop-card">
          <h2>5 Tickets</h2>
          <p>Try out the medium and premium scraping versions with 5 tickets.</p>
          <div className="price">4.99€</div>
          <button onClick={() => handleBuyTickets(5)}>Buy Now</button>
        </div>
        <div className="shop-card">
          <h2>15 Tickets</h2>
          <p>Test medium and premium scraping versions with 15 tickets.</p>
          <div className="price">14.99€</div>
          <button onClick={() => handleBuyTickets(15)}>Buy Now</button>
        </div>
        <div className="shop-card">
          <h2>30 Tickets</h2>
          <p>Experience medium and premium scraping versions with 30 tickets.</p>
          <div className="price">29.99€</div>
          <button onClick={() => handleBuyTickets(30)}>Buy Now</button>
        </div>
      </div>
    </div>
  );
};

export default Shop;
