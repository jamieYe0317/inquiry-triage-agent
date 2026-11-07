### How it works

1. **Input guard (code).** Strips markup, caps the text at 2,000 characters, and flags text that looks like an instruction to an AI. The flag never changes the routing.
2. **Router (LLM).** Returns the type, the sender segment (customer or business), a safety flag, a confidence, and a search query. The inquiry text is data. The router never follows instructions in it.
3. **Retrieval policy (code).** Each type may search only some document sources. For example, a partner request cannot search the returns policy. A confidence below 0.4 sends the case to the Front desk with no lookup.
4. **BM25 search (code).** Finds the 3 best sections in 27 invented manuals, guides, and policies.
5. **Drafter (LLM).** Writes a case summary and a holding reply for a person to edit.
6. **Output guard (code).** Removes any draft that promises a refund, a replacement, a price, a discount, an approval, or partner terms, or that cites a document that the search did not return.
7. **Hand-off rules (code).** Pick the team and the priority. A safety issue is always urgent and is copied to the Quality team.

**Before and after.** By hand, one inquiry takes 10 steps. With the agent, a person does 3: read the case card, check it, and edit and send the reply. This is a step count, not a time measurement.
