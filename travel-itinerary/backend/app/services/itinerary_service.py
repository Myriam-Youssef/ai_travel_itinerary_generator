import uuid
from models.models import ItineraryInput, Itinerary, DayPlan, ItineraryAdjustment
from typing import Dict,List
from db.mongo import db
from bson import ObjectId
from datetime import datetime, timedelta
import re
import os
import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
# from google.genai.types import (
# CreateBatchJobConfig,
# CreateCachedContentConfig,
# EmbedContentConfig,
# FunctionDeclaration,
# GenerateContentConfig,
# Part,
# SafetySetting,
# Tool,
# )

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


# # In-memory "DB"
# fake_db: Dict[str, Itinerary] = {}
def itinerary_to_dict(itinerary: Itinerary) -> dict:
    return {
        "destination": itinerary.destination,
        "start_date": str(itinerary.start_date),
        "end_date": str(itinerary.end_date),
        "interests": itinerary.interests,
        "itinerary": [
            {"day": day.day, "activities": day.activities}
            for day in itinerary.itinerary
        ]
    }

def dict_to_itinerary(id: str, doc: dict) -> Itinerary:
    return Itinerary(
        id=str(id),
        destination=doc["destination"],
        start_date=doc["start_date"],
        end_date=doc["end_date"],
        interests=doc["interests"],
        itinerary=[
            DayPlan(**day) for day in doc["itinerary"]
        ]
    )


async def generate_itinerary_with_gemini(data: ItineraryInput)-> List[DayPlan]:
    try:
        MODEL_ID = "gemini-2.5-flash"
        start_date = data.start_date
        end_date = data.end_date
        num_days = (end_date - start_date).days + 1



        ########### The following equation to calculate the max token is generated by ai:  
        ################################################################################
        # # Adjust max_output_tokens based on the number of days to ensure enough space
        # A rough estimate: 3-4 activities/day * average activity length (e.g., 5-10 words) + JSON overhead
        # For a 7-day trip, 4 activities/day * 10 words/activity = 280 words (approx 350-400 tokens)
        # Add overhead for JSON structure. So 1000 is definitely too low for more than a couple days.
        # Let's set a base minimum and then increase by day
        base_tokens = 500 # for general intro, structure
        tokens_per_day = 150 # estimate for a day's activities + day object
        recommended_max_tokens = max(base_tokens + (num_days * tokens_per_day), 2048) # Ensure at least 2048
        # Cap it at the model's actual max if it goes too high (though unlikely here)
        MODEL_MAX_CAP = 8192 # Maximum for gemini-2.5-flash
        final_max_output_tokens = min(recommended_max_tokens, MODEL_MAX_CAP)



        prompt = f"""
        Create a detailed travel itinerary for {data.destination} from {start_date} to {end_date}.
        
        Trip details:
        - Destination: {data.destination}
        - Duration: {num_days} days
        - Interests: {', '.join(data.interests)}
        
        Please provide a day-by-day itinerary with 3-4 activities per day if it is realistic.
        Format your response as JSON with this structure:
        {{
            "days": [
                {{
                    "day": 1,
                    "activities": ["activity1", "activity2", "activity3"]
                }},
                ...
            ]
        }}
        
        Focus on activities related to: {', '.join(data.interests)}.
        Include realistic timing.
        Make sure to return only valid JSON without any additional text or markdown formatting.
        """

        ai_response = client.models.generate_content(
            model = MODEL_ID,
            contents = prompt,
            config = types.GenerateContentConfig( temperature=0.7,
                                            max_output_tokens = MODEL_MAX_CAP,
                                            )
        )


        print("***************************************************************")
        print(str(ai_response.text))
        if ai_response.candidates:
            print(f"Finish Reason: {ai_response.candidates[0].finish_reason}")
        if ai_response.candidates[0].safety_ratings:
            print(f"Safety Ratings: {ai_response.candidates[0].safety_ratings}")
        if ai_response.prompt_feedback:
            print(f"Prompt Feedback: {ai_response.prompt_feedback}")
        print("***************************************************************")

        if ai_response.text is None:
            # Check for safety ratings if text is None
            if ai_response.prompt_feedback and ai_response.prompt_feedback.block_reason:
                raise Exception(f"Gemini API blocked content: {ai_response.prompt_feedback.block_reason.name} - {ai_response.prompt_feedback.block_reason_message}")
            else:
                raise Exception("Gemini API returned an empty response (ai_response.text is None) without a specific block reason.")

    
        # looks for ```json followed by any charactersuntil ```
        raw_response_text = ai_response.text.strip()
        json_match = re.search(r'```json\n(.*?)```', raw_response_text, re.DOTALL)
        
        cleaned_json_string = ""
        if json_match:
            cleaned_json_string = json_match.group(1).strip()
        else:
            # If no markdown block, assume the entire string should be JSON
            cleaned_json_string = raw_response_text

        try:
            json_response = json.loads(cleaned_json_string) # Use the cleaned string here!
            if "days" in json_response:
                return [DayPlan(**day) for day in json_response["days"]]
            else:
                return []
        except Exception as e:
            raise Exception(f"Error extracting json from ai response: {str(e)}")
        
    except Exception as e:
        raise Exception(f"Error generating itinerary: {str(e)}")


async def generate_itinerary(data: ItineraryInput)-> Itinerary:
    ##dummy gen
    # plan = DayPlan(day=1, 
    #                activities = [f"Explore {data.destination} city center",
    #                              f"Try local {data.interests[0]}"
    #                ])
    # itinerary = Itinerary(
    #     destination=data.destination,
    #     start_date=data.start_date,
    #     end_date=data.end_date,
    #     interests=data.interests,
    #     itinerary=[plan]
    # ) 
    itinerary_plans = await generate_itinerary_with_gemini(data)
    itinerary = Itinerary(
        destination=data.destination,
        start_date=data.start_date,
        end_date=data.end_date,
        interests=data.interests,
        itinerary=itinerary_plans
    ) 
    return itinerary


async def get_itinerary(itinerary_id: str)-> Itinerary:
    try:
        doc = await db.itineraries.find_one({"_id": ObjectId(itinerary_id)})
        if not doc:
             raise Exception("Itinerary not found")
        return dict_to_itinerary(itinerary_id, doc)
    except Exception as e:
        raise Exception(f"Error retrieving itinerary: {str(e)}")


async def get_all_itineraries() -> List[Itinerary]:
    try:
        itineraries = []
        cursor = db.itineraries.find({})
        async for doc in cursor:
            try:
                itinerary = dict_to_itinerary(str(doc["_id"]), doc)
                itineraries.append(itinerary)
            except Exception as e:
                print(f"Error processing document {doc.get('_id', 'unknown')}: {e}")
                continue
        return itineraries
        
    except Exception as e:
        print(f"Error in get_all_itineraries: {str(e)}")
        return []


async def save_itinerary(itinerary: Itinerary) -> Itinerary:
    doc = itinerary_to_dict(itinerary)
    result = await db.itineraries.insert_one(doc)
    itinerary.id = str(result.inserted_id)
    return itinerary


async def delete_itinerary(itinerary_id: str) -> bool:
    try:
        result = await db.itineraries.delete_one({"_id": ObjectId(itinerary_id)})
        return result.deleted_count > 0
    except Exception as e:
        raise Exception(f"Error deleting itinerary: {str(e)}")

async def adjust_itinerary_with_gemini(current_itinerary: Itinerary, adjustment_prompt: str) -> List[DayPlan]:
    try:
        MODEL_ID = "gemini-2.5-flash"
        
        current_plan = ""
        for day in current_itinerary.itinerary:
            current_plan += f"Day {day.day}: {', '.join(day.activities)}\n"
        
        prompt = f"""
        You have a travel itinerary for {current_itinerary.destination} that needs to be adjusted.
        
        Current itinerary:
        {current_plan}
        
        Trip details:
        - Destination: {current_itinerary.destination}
        - Duration: {len(current_itinerary.itinerary)} days
        - Original interests: {', '.join(current_itinerary.interests)}
        
        Please adjust this itinerary based on this request: "{adjustment_prompt}"
        
        Format your response as JSON with this structure:
        {{
            "days": [
                {{
                    "day": 1,
                    "activities": ["activity1", "activity2", "activity3"]
                }},
                ...
            ]
        }}
        
        Keep the same number of days but modify activities according to the request.
        Make sure to return only valid JSON without any additional text or markdown formatting.
        """

        ai_response = client.models.generate_content(
            model=MODEL_ID,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=8192,
            )
        )

        print("***************************************************************")
        print("ADJUSTMENT REQUEST:", adjustment_prompt)
        print("AI RESPONSE:", str(ai_response.text))
        print("***************************************************************")

        if ai_response.text is None:
            raise Exception("Gemini API returned an empty response")

        raw_response_text = ai_response.text.strip()
        json_match = re.search(r'```json\n(.*?)```', raw_response_text, re.DOTALL)
        
        cleaned_json_string = ""
        if json_match:
            cleaned_json_string = json_match.group(1).strip()
        else:
            cleaned_json_string = raw_response_text

        try:
            json_response = json.loads(cleaned_json_string)
            if "days" in json_response:
                return [DayPlan(**day) for day in json_response["days"]]
            else:
                return current_itinerary.itinerary
        except Exception as e:
            raise Exception(f"Error parsing AI response: {str(e)}")
        
    except Exception as e:
        raise Exception(f"Error adjusting itinerary: {str(e)}")


async def adjust_itinerary(itinerary_id: str, adjustment: ItineraryAdjustment) -> Itinerary:
    try:
        current_itinerary = await get_itinerary(itinerary_id)
        adjusted_plans = await adjust_itinerary_with_gemini(current_itinerary, adjustment.adjustment_prompt)
        
        updated_itinerary = Itinerary(
            id=current_itinerary.id,
            destination=current_itinerary.destination,
            start_date=current_itinerary.start_date,
            end_date=current_itinerary.end_date,
            interests=current_itinerary.interests,
            itinerary=adjusted_plans
        )
        
        doc = itinerary_to_dict(updated_itinerary)
        doc["updated_at"] = datetime.now().isoformat()
        
        result = await db.itineraries.update_one(
            {"_id": ObjectId(itinerary_id)},
            {"$set": doc}
        )
        
        if result.matched_count == 0:
            raise Exception("Itinerary not found")
        
        return updated_itinerary
        
    except Exception as e:
        raise Exception(f"Error adjusting itinerary: {str(e)}")
