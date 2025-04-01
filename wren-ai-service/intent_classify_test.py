from typing import Any

from dotenv import load_dotenv

from src.pipelines.generation.intent_classification import (
    intent_classification_system_prompt,
)
from src.providers.llm.litellm import LitellmLLMProvider

load_dotenv(dotenv_path="docker/.env")


provider = LitellmLLMProvider(
    model="gpt-4o-mini",
    api_key_name="MONICA_API_KEY",
    api_base="https://openapi.monica.im/v1",
    timeout=120.0,
    kwargs={
        "temperature": 0,
        "max_tokens": 4096,
        "top_p": 1,
        "frequency_penalty": 0,
        "presence_penalty": 0,
        "stop": None,
    },
)

user_prompt = {
    "prompt": """
### DATABASE SCHEMA ###

    
/* {'alias': 'order reviews', 'description': 'This table contains customer reviews for each order, including feedback comments, ratings, and timestamps for when the review was submitted and responded to. It helps track customer satisfaction and review management on the e-commerce platform.'} */
CREATE TABLE olist_order_reviews_dataset (
  -- {"alias":"review_id","description":"Unique identifier for the specific review entry."}
  review_id VARCHAR PRIMARY KEY,
  -- {"alias":"order_id","description":"Unique identifier linking the review to the corresponding order."}
  order_id VARCHAR,
  -- {"alias":"review_score","description":"Numeric rating given by the customer, typically ranging from 1 (worst) to 5 (best)."}
  review_score BIGINT,
  -- {"alias":"review_comment_title","description":"Summary or title of the customer's review"}
  review_comment_title VARCHAR,
  -- {"alias":"review_comment_message","description":"Detailed feedback or comments provided by the customer regarding the order."}
  review_comment_message VARCHAR,
  -- {"alias":"review_creation_date","description":"Date and time when the customer initially submitted the review."}
  review_creation_date TIMESTAMP,
  -- {"alias":"review_answer_timestamp","description":"Date and time when the review was responded to by the seller"}
  review_answer_timestamp TIMESTAMP,
  -- {"condition": "olist_orders_dataset".order_id = "olist_order_reviews_dataset".order_id, "joinType": ONE_TO_MANY}
  FOREIGN KEY (order_id) REFERENCES olist_orders_dataset(order_id)
);

    
/* {'alias': 'orders', 'description': 'This table contains detailed information about customer orders, including timestamps for various stages of the order process (approval, shipping, delivery), as well as the order status and customer identification. It helps track the lifecycle of an order from purchase to delivery.'} */
CREATE TABLE olist_orders_dataset (
  -- {"alias":"order_id","description":"Unique identifier for the specific order"}
  order_id VARCHAR PRIMARY KEY,
  -- {"alias":"customer_id","description":"Unique identifier for the customer who placed the order."}
  customer_id VARCHAR,
  -- {"alias":"order_status","description":"Current status of the order (e.g., delivered, shipped, canceled)."}
  order_status VARCHAR,
  -- {"alias":"order_purchase_timestamp","description":"Date and time when the order was placed by the customer."}
  order_purchase_timestamp TIMESTAMP,
  -- {"alias":"order_approved_at","description":"Date and time when the order was approved for processing."}
  order_approved_at TIMESTAMP,
  -- {"alias":"order_delivered_carrier_date","description":"Date when the order was handed over to the carrier or freight forwarder for delivery."}
  order_delivered_carrier_date TIMESTAMP,
  -- {"alias":"order_delivered_customer_date","description":"Date when the order was delivered to the customer."}
  order_delivered_customer_date TIMESTAMP,
  -- {"alias":"order_estimated_delivery_date","description":"Expected delivery date based on the initial estimate."}
  order_estimated_delivery_date TIMESTAMP,
  -- {"condition": "olist_orders_dataset".customer_id = "olist_customers_dataset".customer_id, "joinType": MANY_TO_ONE}
  FOREIGN KEY (customer_id) REFERENCES olist_customers_dataset(customer_id),
  -- {"condition": "olist_orders_dataset".order_id = "olist_order_items_dataset".order_id, "joinType": ONE_TO_MANY}
  FOREIGN KEY (order_id) REFERENCES olist_order_items_dataset(order_item_id),
  -- {"condition": "olist_orders_dataset".order_id = "olist_order_reviews_dataset".order_id, "joinType": ONE_TO_MANY}
  FOREIGN KEY (order_id) REFERENCES olist_order_reviews_dataset(review_id),
  -- {"condition": "olist_orders_dataset".order_id = "olist_order_payments_dataset".order_id, "joinType": ONE_TO_MANY}
  FOREIGN KEY (order_id) REFERENCES olist_order_payments_dataset(order_id)
);

    
/* {'alias': 'geolocation', 'description': 'This table contains detailed information about Brazilian zip codes and their corresponding latitude and longitude coordinates. It can be used to plot maps, calculate distances between sellers and customers, and perform geographic analysis.'} */
CREATE TABLE olist_geolocation_dataset (
  -- {"alias":"geolocation_zip_code_prefix","description":"First 5 digits of zip code"}
  geolocation_zip_code_prefix VARCHAR,
  -- {"alias":"geolocation_lat","description":"The coordinations for the locations latitude"}
  geolocation_lat DOUBLE,
  -- {"alias":"geolocation_lng","description":"The coordinations for the locations longitude"}
  geolocation_lng DOUBLE,
  -- {"alias":"geolocation_city","description":"The city name of the geolocation"}
  geolocation_city VARCHAR,
  -- {"alias":"geolocation_state","description":"The state of the geolocation"}
  geolocation_state VARCHAR,
  -- {"condition": "olist_geolocation_dataset".geolocation_zip_code_prefix = "olist_customers_dataset".customer_zip_code_prefix, "joinType": ONE_TO_MANY}
  FOREIGN KEY (geolocation_zip_code_prefix) REFERENCES olist_customers_dataset(customer_id),
  -- {"condition": "olist_geolocation_dataset".geolocation_zip_code_prefix = "olist_sellers_dataset".seller_zip_code_prefix, "joinType": ONE_TO_MANY}
  FOREIGN KEY (geolocation_zip_code_prefix) REFERENCES olist_sellers_dataset()
);

    
/* {'alias': 'customers', 'description': ''} */
CREATE TABLE olist_customers_dataset (
  -- {"alias":"customer_id","description":""}
  customer_id VARCHAR PRIMARY KEY,
  -- {"alias":"customer_unique_id","description":"Unique id of the customer"}
  customer_unique_id VARCHAR,
  -- {"alias":"customer_zip_code_prefix","description":"First 5 digits of customer zip code"}
  customer_zip_code_prefix VARCHAR,
  -- {"alias":"customer_city","description":"Name of the city where the customer is located"}
  customer_city VARCHAR,
  -- {"alias":"customer_state","description":"Name of the state where the customer is located"}
  customer_state VARCHAR,
  -- {"condition": "olist_orders_dataset".customer_id = "olist_customers_dataset".customer_id, "joinType": MANY_TO_ONE}
  FOREIGN KEY (customer_id) REFERENCES olist_orders_dataset(order_id),
  -- {"condition": "olist_geolocation_dataset".geolocation_zip_code_prefix = "olist_customers_dataset".customer_zip_code_prefix, "joinType": ONE_TO_MANY}
  FOREIGN KEY (customer_zip_code_prefix) REFERENCES olist_geolocation_dataset()
);

    
/* {'alias': 'sellers', 'description': 'This table includes data about the sellers that fulfilled orders made. Use it to find the seller location and to identify which seller fulfilled each product.'} */
CREATE TABLE olist_sellers_dataset (
  -- {"alias":"seller_id","description":"Unique identifier for the seller on the platform"}
  seller_id VARCHAR,
  -- {"alias":"seller_zip_code_prefix","description":"First 5 digits of seller zip code"}
  seller_zip_code_prefix VARCHAR,
  -- {"alias":"seller_city","description":"The Brazilian city where the seller is located"}
  seller_city VARCHAR,
  -- {"alias":"seller_state","description":"The Brazilian state where the seller is located"}
  seller_state VARCHAR,
  -- {"condition": "olist_order_items_dataset".seller_id = "olist_sellers_dataset".seller_id, "joinType": MANY_TO_ONE}
  FOREIGN KEY (seller_id) REFERENCES olist_order_items_dataset(order_item_id),
  -- {"condition": "olist_geolocation_dataset".geolocation_zip_code_prefix = "olist_sellers_dataset".seller_zip_code_prefix, "joinType": ONE_TO_MANY}
  FOREIGN KEY (seller_zip_code_prefix) REFERENCES olist_geolocation_dataset()
);

    
/* {'alias': 'order items', 'description': 'This table contains the information related to a specific order containing its shipping cost, products, cost, number of order items, and the seller.'} */
CREATE TABLE olist_order_items_dataset (
  -- {"alias":"order_id","description":"Unique identifier for the order across the platform"}
  order_id VARCHAR,
  -- {"alias":"order_item_id","description":"Unique identifier for each item within a specific order"}
  order_item_id BIGINT PRIMARY KEY,
  -- {"alias":"product_id","description":"Unique identifier for the product sold in the order."}
  product_id VARCHAR,
  -- {"alias":"seller_id","description":"Unique identifier of the seller who fulfilled the order item."}
  seller_id VARCHAR,
  -- {"alias":"shipping_limit_date","description":"Deadline for the order item to be shipped by the seller."}
  shipping_limit_date TIMESTAMP,
  -- {"alias":"price","description":"Price of the individual item within the order"}
  price DOUBLE,
  -- {"alias":"freight_value","description":"Cost of shipping associated with the specific order item"}
  freight_value DOUBLE,
  -- {"condition": "olist_orders_dataset".order_id = "olist_order_items_dataset".order_id, "joinType": ONE_TO_MANY}
  FOREIGN KEY (order_id) REFERENCES olist_orders_dataset(order_id),
  -- {"condition": "olist_order_items_dataset".product_id = "olist_products_dataset".product_id, "joinType": MANY_TO_ONE}
  FOREIGN KEY (product_id) REFERENCES olist_products_dataset(product_id),
  -- {"condition": "olist_order_items_dataset".seller_id = "olist_sellers_dataset".seller_id, "joinType": MANY_TO_ONE}
  FOREIGN KEY (seller_id) REFERENCES olist_sellers_dataset()
);

    
/* {'alias': 'products', 'description': 'This table provides detailed information about products, including their category, dimensions, weight, description length, and the number of photos. This helps in managing product details and enhancing the shopping experience on the e-commerce platform.'} */
CREATE TABLE olist_products_dataset (
  -- {"alias":"product_id","description":"Unique identifier for the product"}
  product_id VARCHAR PRIMARY KEY,
  -- {"alias":"product_category_name","description":"Name of the product category to which the item belongs."}
  product_category_name VARCHAR,
  -- {"alias":"product_name_lenght","description":"Length of the product name in characters"}
  product_name_lenght BIGINT,
  -- {"alias":"product_description_lenght","description":"Length of the product description in characters."}
  product_description_lenght BIGINT,
  -- {"alias":"product_photos_qty","description":"Number of photos available for the product"}
  product_photos_qty BIGINT,
  -- {"alias":"product_weight_g","description":"Weight of the product in grams"}
  product_weight_g BIGINT,
  -- {"alias":"product_length_cm","description":"Length of the product in centimeters"}
  product_length_cm BIGINT,
  -- {"alias":"product_height_cm","description":"Height of the product in centimeters."}
  product_height_cm BIGINT,
  -- {"alias":"product_width_cm","description":"Width of the product in centimeters"}
  product_width_cm BIGINT,
  -- {"condition": "olist_order_items_dataset".product_id = "olist_products_dataset".product_id, "joinType": MANY_TO_ONE}
  FOREIGN KEY (product_id) REFERENCES olist_order_items_dataset(order_item_id),
  -- {"condition": "product_category_name_translation".product_category_name = "olist_products_dataset".product_category_name, "joinType": ONE_TO_MANY}
  FOREIGN KEY (product_category_name) REFERENCES product_category_name_translation(product_category_name)
);

    
/* {'alias': 'order payments', 'description': 'This table contains information about payment details for each order, including payment methods, amounts, installment plans, and payment sequences, helping to track how orders were paid and processed within the e-commerce platform.'} */
CREATE TABLE olist_order_payments_dataset (
  -- {"alias":"order_id","description":"Unique identifier for the order associated with the payment."}
  order_id VARCHAR PRIMARY KEY,
  -- {"alias":"payment_sequential","description":"Sequence number for tracking multiple payments within the same order."}
  payment_sequential BIGINT,
  -- {"alias":"payment_type","description":"Method used for the payment, such as credit card, debit, or voucher."}
  payment_type VARCHAR,
  -- {"alias":"payment_installments","description":"Number of installments the payment is divided into for the order."}
  payment_installments BIGINT,
  -- {"alias":"payment_value","description":"Total amount paid in the specific transaction."}
  payment_value DOUBLE,
  -- {"condition": "olist_orders_dataset".order_id = "olist_order_payments_dataset".order_id, "joinType": ONE_TO_MANY}
  FOREIGN KEY (order_id) REFERENCES olist_orders_dataset(order_id)
);

    
/* {'alias': 'product category name translation', 'description': 'This table contains translations of product categories from Portuguese to English.'} */
CREATE TABLE product_category_name_translation (
  -- {"alias":"product_category_name","description":"Original name of the product category in Portuguese."}
  product_category_name VARCHAR PRIMARY KEY,
  -- {"alias":"product_category_name_english","description":"Translated name of the product category in English."}
  product_category_name_english VARCHAR,
  -- {"condition": "product_category_name_translation".product_category_name = "olist_products_dataset".product_category_name, "joinType": ONE_TO_MANY}
  FOREIGN KEY (product_category_name) REFERENCES olist_products_dataset(product_id)
);








### QUESTION ###
User's question: What is the average score of reviews submitted for orders placed by customers in each city?
Current Time: 2025-04-01 Tuesday 08:49:30
Output Language: English

Let's think step by step
"""
}


async def classify_intent(prompt: dict, generator: Any) -> dict:
    return await generator(prompt=prompt.get("prompt"))


async def main():
    generator = provider.get_generator(system_prompt=intent_classification_system_prompt)
    print("generator")
    result = await classify_intent(user_prompt, generator)
    print(result)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
