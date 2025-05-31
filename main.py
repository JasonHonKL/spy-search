from src.model.gemini import Gemini


m = Gemini("gemini-2.0-flash")
from src.agent.planner import Planner

p  = Planner(m, "search information about agent")
p.add_model("vision" , "allow agent to visially read the screen")
p.add_model("searcher" , "allow agent to do google search")
p.add_model("retirival" , "allow agnet to retrival infomation with vector db , or add new info to the vector db")
res = p.run(p.query)

