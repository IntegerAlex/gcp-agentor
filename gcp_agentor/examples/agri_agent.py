"""
AgriAgent Example

Sample agents for agricultural advisory system.
"""

from typing import Dict, Any, List, Optional
from ..invoker import BaseAgent


class CropAdvisorAgent(BaseAgent):
    """
    Crop Advisor Agent
    
    Provides crop recommendations based on weather, soil, and season.
    """
    
    def __init__(self):
        """Initialize the crop advisor agent."""
        self.name = "CropAdvisor"
        self.crop_database = {
            "monsoon": {
                "rice": {"description": "Best for monsoon season", "duration": "120 days"},
                "maize": {"description": "Good monsoon crop", "duration": "90 days"},
                "cotton": {"description": "Suitable for monsoon", "duration": "150 days"}
            },
            "winter": {
                "wheat": {"description": "Primary winter crop", "duration": "120 days"},
                "mustard": {"description": "Oil seed crop", "duration": "90 days"},
                "potato": {"description": "Winter vegetable", "duration": "100 days"}
            },
            "summer": {
                "millet": {"description": "Drought resistant", "duration": "80 days"},
                "pulses": {"description": "Legume crops", "duration": "90 days"},
                "vegetables": {"description": "Short duration crops", "duration": "60 days"}
            }
        }
    
    def invoke(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Provide crop advice based on the message and context.
        
        Args:
            message: User message
            context: Context information
            
        Returns:
            Crop advice response
        """
        context = context or {}
        
        # Extract season from context or message
        season = context.get("season", "monsoon")
        location = context.get("location", "unknown")
        soil_ph = context.get("soil_pH", 6.5)
        
        # Simple keyword-based season detection
        message_lower = message.lower()
        if any(word in message_lower for word in ["monsoon", "rain", "wet"]):
            season = "monsoon"
        elif any(word in message_lower for word in ["winter", "cold", "cool"]):
            season = "winter"
        elif any(word in message_lower for word in ["summer", "hot", "dry"]):
            season = "summer"
        
        # Get crop recommendations
        if season in self.crop_database:
            crops = self.crop_database[season]
            recommendations = []
            
            for crop, info in crops.items():
                recommendations.append(f"• {crop.title()}: {info['description']} ({info['duration']})")
            
            response = f"🌾 Crop Recommendations for {season.title()} Season in {location}:\n\n"
            response += "\n".join(recommendations)
            response += f"\n\n💡 Soil pH: {soil_ph} (Optimal range: 6.0-7.5)"
            
            return response
        else:
            return f"Sorry, I don't have crop recommendations for {season} season."
    
    def get_crop_info(self, crop_name: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific crop.
        
        Args:
            crop_name: Name of the crop
            
        Returns:
            Crop information dictionary
        """
        for season, crops in self.crop_database.items():
            if crop_name.lower() in crops:
                return {
                    "crop": crop_name,
                    "season": season,
                    **crops[crop_name.lower()]
                }
        return {"error": f"Crop {crop_name} not found in database"}


class WeatherAgent(BaseAgent):
    """
    Weather Agent
    
    Provides weather information and forecasts.
    """
    
    def __init__(self):
        """Initialize the weather agent."""
        self.name = "WeatherBot"
        self.weather_data = {
            "Jalgaon": {
                "current": {"temperature": 28, "humidity": 65, "condition": "Partly Cloudy"},
                "forecast": [
                    {"day": "Today", "high": 30, "low": 22, "condition": "Partly Cloudy"},
                    {"day": "Tomorrow", "high": 32, "low": 24, "condition": "Sunny"},
                    {"day": "Day 3", "high": 29, "low": 21, "condition": "Light Rain"}
                ]
            },
            "Mumbai": {
                "current": {"temperature": 32, "humidity": 80, "condition": "Humid"},
                "forecast": [
                    {"day": "Today", "high": 34, "low": 26, "condition": "Humid"},
                    {"day": "Tomorrow", "high": 33, "low": 25, "condition": "Partly Cloudy"},
                    {"day": "Day 3", "high": 31, "low": 24, "condition": "Rain"}
                ]
            }
        }
    
    def invoke(self, message: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Provide weather information based on the message and context.
        
        Args:
            message: User message
            context: Context information
            
        Returns:
            Weather information response
        """
        context = context or {}
        
        # Extract location from context or message
        location = context.get("location", "Jalgaon")
        
        # Simple location detection from message
        message_lower = message.lower()
        if "mumbai" in message_lower:
            location = "Mumbai"
        elif "jalgaon" in message_lower:
            location = "Jalgaon"
        
        if location in self.weather_data:
            weather = self.weather_data[location]
            current = weather["current"]
            forecast = weather["forecast"]
            
            response = f"🌤️ Weather for {location}:\n\n"
            response += f"Current: {current['temperature']}°C, {current['humidity']}% humidity, {current['condition']}\n\n"
            response += "3-Day Forecast:\n"
            
            for day in forecast:
                response += f"• {day['day']}: {day['high']}°C / {day['low']}°C, {day['condition']}\n"
            
            return response
        else:
            return f"Sorry, I don't have weather data for {location}. Available locations: {', '.join(self.weather_data.keys())}"
    
    def get_weather_alert(self, location: str) -> str:
        """
        Get weather alerts for a location.
        
        Args:
            location: Location name
            
        Returns:
            Weather alert message
        """
        if location == "Mumbai":
            return "⚠️ Weather Alert: Heavy rainfall expected in next 24 hours. Take necessary precautions."
        elif location == "Jalgaon":
            return "ℹ️ Weather Info: Normal weather conditions expected. Good for farming activities."
        else:
            return f"No weather alerts available for {location}"


class PestAssistantAgent(BaseAgent):
    """
    Pest Assistant Agent
    
    Provides pest control advice and treatment recommendations.
    """
    
    def __init__(self):
        """Initialize the pest assistant agent."""
        self.name = "PestAssistant"
        self.pest_database = {
            "rice": {
                "pests": [
                    {
                        "name": "Rice Stem Borer",
                        "symptoms": "Dead hearts, white ears",
                        "treatment": "Use neem-based pesticides, maintain field hygiene"
                    },
                    {
                        "name": "Rice Leaf Folder",
                        "symptoms": "Rolled leaves, reduced photosynthesis",
                        "treatment": "Apply carbaryl or quinalphos, remove alternate hosts"
                    }
                ]
            },
            "wheat": {
                "pests": [
                    {
                        "name": "Aphids",
                        "symptoms": "Yellowing leaves, stunted growth",
                        "treatment": "Use imidacloprid, encourage natural predators"
                    },
                    {
                        "name": "Army Worm",
                        "symptoms": "Defoliation, skeletonized leaves",
                        "treatment": "Apply chlorpyriphos, monitor regularly"
                    }
                ]
            },
            "cotton": {
                "pests": [
                    {
                        "name": "Bollworm",
                        "symptoms": "Damaged bolls, reduced yield",
                        "treatment": "Use Bt cotton, apply recommended insecticides"
                    },
                    {
                        "name": "Whitefly",
                        "symptoms": "Yellowing, sooty mold",
                        "treatment": "Use systemic insecticides, remove weeds"
                    }
                ]
            }
        }
    
    def invoke(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Provide pest control advice based on the message and context.
        
        Args:
            message: User message
            context: Context information
            
        Returns:
            Pest control advice response
        """
        context = context or {}
        
        # Extract crop from context or message
        crop = context.get("crop", "rice")
        
        # Simple crop detection from message
        message_lower = message.lower()
        if "wheat" in message_lower:
            crop = "wheat"
        elif "cotton" in message_lower:
            crop = "cotton"
        elif "rice" in message_lower:
            crop = "rice"
        
        if crop in self.pest_database:
            pests = self.pest_database[crop]
            
            response = f"🐛 Pest Management for {crop.title()}:\n\n"
            
            for pest in pests["pests"]:
                response += f"**{pest['name']}**\n"
                response += f"Symptoms: {pest['symptoms']}\n"
                response += f"Treatment: {pest['treatment']}\n\n"
            
            response += "💡 General Tips:\n"
            response += "• Monitor crops regularly\n"
            response += "• Use integrated pest management\n"
            response += "• Maintain field hygiene\n"
            response += "• Consider biological control methods"
            
            return response
        else:
            return f"Sorry, I don't have pest information for {crop}. Available crops: {', '.join(self.pest_database.keys())}"
    
    def get_pest_alert(self, crop: str, severity: str = "medium") -> str:
        """
        Get pest alert for a specific crop.
        
        Args:
            crop: Crop name
            severity: Alert severity (low, medium, high)
            
        Returns:
            Pest alert message
        """
        if crop == "rice" and severity == "high":
            return "🚨 High Alert: Rice Stem Borer infestation detected in nearby areas. Monitor your crop closely."
        elif crop == "cotton":
            return "⚠️ Alert: Bollworm activity increasing. Consider preventive measures."
        else:
            return f"ℹ️ Normal pest activity expected for {crop}. Continue regular monitoring."


class SoilAnalyzerAgent(BaseAgent):
    """
    Soil Analyzer Agent
    
    Provides soil analysis and fertilizer recommendations.
    """
    
    def __init__(self):
        """Initialize the soil analyzer agent."""
        self.name = "SoilAnalyzer"
        self.soil_recommendations = {
            "acidic": {
                "ph_range": "5.0-6.0",
                "recommendations": [
                    "Add lime to raise pH",
                    "Use calcium-rich fertilizers",
                    "Consider dolomite application"
                ]
            },
            "neutral": {
                "ph_range": "6.0-7.5",
                "recommendations": [
                    "Optimal pH for most crops",
                    "Use balanced NPK fertilizers",
                    "Maintain organic matter"
                ]
            },
            "alkaline": {
                "ph_range": "7.5-8.5",
                "recommendations": [
                    "Add sulfur to lower pH",
                    "Use acid-forming fertilizers",
                    "Consider gypsum application"
                ]
            }
        }
    
    def invoke(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Provide soil analysis and recommendations.
        
        Args:
            message: User message
            context: Context information
            
        Returns:
            Soil analysis response
        """
        context = context or {}
        
        # Extract soil pH from context
        soil_ph = context.get("soil_pH", 6.5)
        
        # Determine soil type
        if soil_ph < 6.0:
            soil_type = "acidic"
        elif soil_ph <= 7.5:
            soil_type = "neutral"
        else:
            soil_type = "alkaline"
        
        recommendations = self.soil_recommendations[soil_type]
        
        response = f"🌱 Soil Analysis Report:\n\n"
        response += f"pH Level: {soil_ph} ({soil_type.title()})\n"
        response += f"Optimal Range: {recommendations['ph_range']}\n\n"
        response += "Recommendations:\n"
        
        for rec in recommendations["recommendations"]:
            response += f"• {rec}\n"
        
        response += f"\n💡 Additional Tips:\n"
        response += "• Test soil regularly\n"
        response += "• Maintain proper drainage\n"
        response += "• Use organic amendments\n"
        response += "• Rotate crops to improve soil health"
        
        return response


class MarketAgent(BaseAgent):
    """
    Market Agent
    
    Provides market prices and trading information.
    """
    
    def __init__(self):
        """Initialize the market agent."""
        self.name = "MarketAgent"
        self.price_data = {
            "rice": {"current": 2800, "unit": "per quintal", "trend": "stable"},
            "wheat": {"current": 2200, "unit": "per quintal", "trend": "rising"},
            "cotton": {"current": 6500, "unit": "per quintal", "trend": "falling"},
            "maize": {"current": 1800, "unit": "per quintal", "trend": "stable"},
            "pulses": {"current": 4500, "unit": "per quintal", "trend": "rising"}
        }
    
    def invoke(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Provide market price information.
        
        Args:
            message: User message
            context: Context information
            
        Returns:
            Market information response
        """
        context = context or {}
        
        # Extract crop from context or message
        crop = context.get("crop", "rice")
        
        # Simple crop detection from message
        message_lower = message.lower()
        for available_crop in self.price_data.keys():
            if available_crop in message_lower:
                crop = available_crop
                break
        
        if crop in self.price_data:
            price_info = self.price_data[crop]
            
            response = f"📊 Market Information for {crop.title()}:\n\n"
            response += f"Current Price: ₹{price_info['current']} {price_info['unit']}\n"
            response += f"Market Trend: {price_info['trend'].title()}\n\n"
            
            if price_info['trend'] == "rising":
                response += "📈 Price is trending upward - good time to sell\n"
            elif price_info['trend'] == "falling":
                response += "📉 Price is trending downward - consider holding\n"
            else:
                response += "➡️ Price is stable - normal trading conditions\n"
            
            response += f"\n💡 Trading Tips:\n"
            response += "• Monitor daily price updates\n"
            response += "• Consider storage costs\n"
            response += "• Check government MSP rates\n"
            response += "• Plan harvest timing carefully"
            
            return response
        else:
            available_crops = ", ".join(self.price_data.keys())
            return f"Sorry, I don't have price data for {crop}. Available crops: {available_crops}"


class GeneralAssistantAgent(BaseAgent):
    """
    General Assistant Agent
    
    Provides general agricultural advice and information.
    """
    
    def __init__(self):
        """Initialize the general assistant agent."""
        self.name = "GeneralAssistant"
        self.general_tips = {
            "farming_basics": [
                "Always test soil before planting",
                "Use crop rotation to maintain soil health",
                "Implement proper irrigation practices",
                "Monitor weather forecasts regularly"
            ],
            "sustainable_farming": [
                "Use organic fertilizers when possible",
                "Implement integrated pest management",
                "Conserve water through efficient irrigation",
                "Maintain biodiversity on your farm"
            ],
            "technology": [
                "Consider precision farming techniques",
                "Use mobile apps for crop monitoring",
                "Explore IoT sensors for soil monitoring",
                "Stay updated with agricultural innovations"
            ]
        }
    
    def invoke(self, message: str, context: Dict[str, Any] = None) -> str:
        """
        Provide general agricultural advice.
        
        Args:
            message: User message
            context: Context information
            
        Returns:
            General advice response
        """
        context = context or {}
        
        message_lower = message.lower()
        
        # Determine topic based on keywords
        if any(word in message_lower for word in ["basic", "beginner", "start"]):
            topic = "farming_basics"
            title = "Farming Basics"
        elif any(word in message_lower for word in ["sustainable", "organic", "environment"]):
            topic = "sustainable_farming"
            title = "Sustainable Farming"
        elif any(word in message_lower for word in ["technology", "digital", "smart"]):
            topic = "technology"
            title = "Agricultural Technology"
        else:
            # Default to farming basics
            topic = "farming_basics"
            title = "General Agricultural Advice"
        
        tips = self.general_tips[topic]
        
        response = f"🌾 {title}:\n\n"
        
        for i, tip in enumerate(tips, 1):
            response += f"{i}. {tip}\n"
        
        response += f"\n💡 Need specific advice? Try asking about:\n"
        response += "• Crop recommendations\n"
        response += "• Weather information\n"
        response += "• Pest control\n"
        response += "• Soil analysis\n"
        response += "• Market prices"
        
        return response 