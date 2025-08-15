-- Q1
SELECT p.City,
       COUNT(DISTINCT p.Provider_ID) AS provider_count,
       COUNT(DISTINCT r.Receiver_ID) AS receiver_count
FROM provider_data p
LEFT JOIN receiver_data r ON p.City = r.City
GROUP BY p.City;

--Q2
SELECT city, 
	COUNT(DISTINCT provider_id) AS total_providers,
    COUNT(DISTINCT receiver_id) AS total_receivers
FROM (
      SELECT city, provider_id, NULL::int AS receiver_id FROM provider_data
      UNION ALL
      SELECT city, NULL::int AS provider_id, receiver_id FROM receiver_data
) t
GROUP BY city
ORDER BY city;

--Q3
SELECT Provider_Type, SUM(Quantity) AS total_donated
FROM food_data
GROUP BY Provider_Type
ORDER BY total_donated DESC;

--Q4
SELECT provider_type, SUM(f.quantity) AS total_quantity
FROM food_data f
JOIN provider_data p ON f.provider_id = p.provider_id
GROUP BY provider_type
ORDER BY total_quantity DESC;

--Q5
SELECT r.Name, r.City, SUM(f.Quantity) AS total_claimed
FROM claim_data c
JOIN receiver_data r ON c.Receiver_ID = r.Receiver_ID
JOIN food_data f ON c.Food_ID = f.Food_ID
GROUP BY r.Name, r.City
ORDER BY total_claimed DESC;

--Q6
SELECT SUM(Quantity) AS total_food_available
FROM food_data;

--Q7
SELECT Location, COUNT(*) AS listing_count
FROM food_data
GROUP BY Location
ORDER BY listing_count DESC;

--Q8
SELECT Food_Type, COUNT(*) AS count_available
FROM food_data
GROUP BY Food_Type
ORDER BY count_available DESC;

--Q9
SELECT f.Food_Name, COUNT(c.Claim_ID) AS total_claims
FROM claim_data c
JOIN food_data f ON c.Food_ID = f.Food_ID
GROUP BY f.Food_Name
ORDER BY total_claims DESC;

--Q10
SELECT p.Name as donor, COUNT(c.Claim_ID) AS successful_donate
FROM claim_data c
JOIN food_data f ON c.Food_ID = f.Food_ID
JOIN provider_data p ON f.Provider_ID = p.Provider_ID
WHERE c.Status = 'Completed'
GROUP BY p.Name
ORDER BY successful_donate DESC;

--Q11
SELECT Status,
       ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claim_data), 2) AS percentage
FROM claim_data
GROUP BY Status;

--Q12
SELECT r.Name, ROUND(AVG(f.Quantity), 2) AS avg_qty_claimed
FROM claim_data c
JOIN receiver_data r ON c.Receiver_ID = r.Receiver_ID
JOIN food_data f ON c.Food_ID = f.Food_ID
GROUP BY r.Name
ORDER BY avg_qty_claimed DESC;

--Q13
SELECT Meal_Type, COUNT(*) AS total_claims
FROM claim_data c
JOIN food_data f ON c.Food_ID = f.Food_ID
GROUP BY Meal_Type
ORDER BY total_claims DESC;

--Q14
SELECT p.Name, SUM(f.Quantity) AS total_qty_donated
FROM food_data f
JOIN provider_data p ON f.Provider_ID = p.Provider_ID
GROUP BY p.Name
ORDER BY total_qty_donated DESC;

--Q15
SELECT r.City, COUNT(c.Claim_ID) AS total_claims
FROM claim_data c
JOIN receiver_data r ON c.Receiver_ID = r.Receiver_ID
GROUP BY r.City
ORDER BY total_claims DESC;

--Q16
SELECT Location, COUNT(*) AS wasted_items
FROM food_data
WHERE Expiry_Date < CURRENT_DATE
GROUP BY Location
ORDER BY wasted_items DESC;

--Q17
SELECT p.name,
       COUNT(*) AS total_claims,
       SUM(f.quantity) AS total_quantity
FROM food_data f
JOIN provider_data p 
    ON f.provider_id = p.provider_id
GROUP BY p.name
ORDER BY total_quantity DESC;

--Q18
SELECT f.location,
       COUNT(*) AS total_claims,
       SUM(f.quantity) AS total_quantity
FROM food_data f
GROUP BY f.location
ORDER BY total_quantity DESC;


