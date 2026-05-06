export const serverUrl = process.env.REACT_APP_SERVER_URL || 'http://127.0.0.1:4000';
export const target_language = process.env.REACT_APP_TARGET_LANGUAGE || "English"
export const contact_name = process.env.REACT_APP_CONTACT_NAME || "Research Team"
export const contact_email = process.env.REACT_APP_CONTACT_EMAIL || "research-team@example.com"

export const contact_address = "University of Cambridge"
export const experiment_title = "Healthcare Dialogue Collection Experiment"

export const colour_array = ['#ECECEC',   '#B80000', '#DB3E00', '#FCCB00', '#008B02', '#006B76', '#1273DE', '#004DCF', '#5300EB',
    '#EB9694', '#FAD0C3', '#FEF3BD', '#C1E1C5', '#BEDADC', '#C4DEF6', '#BED3F3', '#D4C4FB']


export const system_colour = ["gray", "#ECECEC"]
export const user_colour = ["#008B02", "#C8E6C9"]


export const exampleTask = {
    "language": "ENG",
    "task_id": "ENG_EXAMPLE_1",
    "utterance": [
        {
            "role": "Assistant",
            "generated_text": "Good morning! I'm your AI healthcare assistant. How can I assist you today?",
            "instruction": "",
            "snippet": [],
            "out_of_knowledge": false
        },
        {
            "role": "Patient",
            "generated_text": "Hi system! I have some question about traditional medicine, could you help me?",
            "instruction": "Greet the assistant and mention that you have questions about traditional medicine. Ask if the assistant can help.",
            "snippet": [],
            "out_of_knowledge": false
        },
        {
            "role": "Assistant",
            "generated_text": "My pleasure! Could you tell me more about your question?",
            "instruction": "",
            "snippet": [],
            "out_of_knowledge": false
        },
        {
            "role": "Patient",
            "generated_text": "I’ve heard a lot about traditional medicine and I’m curious. What exactly is it?",
            "instruction": "Explain that you’ve heard a lot about traditional medicine and express curiosity about what it is. Ask for a definition.",
            "snippet": [],
            "out_of_knowledge": false
        },
        {
            "role": "Assistant",
            "generated_text": "Traditional medicine refers to the knowledge, skills, and practices based on the theories, beliefs, and experiences indigenous to different cultures, used in the maintenance of health, as well as in the prevention, diagnosis, improvement, or treatment of physical and mental illnesses.",
            "instruction": "",
            "snippet": [
                {
                    "url": "https://www.who.int/news-room/questions-and-answers/item/traditional-medicine",
                    "language": "ENG",
                    "data": {
                        "type": "qa_pair",
                        "topic": "traditional medicine",
                        "title": "What is traditional medicine?",
                        "content": "Traditional medicine has a long history. It is the sum of the knowledge, skills and practices based on the theories, beliefs and experiences indigenous to different cultures, whether explicable or not, used in the maintenance of health and the prevention, diagnosis, improvement or treatment of physical and mental illness.\n See WHO definitions of traditional, complementary and herbal medicines."
                    },
                    "parallel_data": false,
                    "parallel_identifier": "traditional-medicine-qa1",
                    "unique_identifier": "traditional-medicine-qa1"
                }
            ],
            "out_of_knowledge": false
        },
        {
            "role": "Patient",
            "generated_text": "That sounds comprehensive. Is it safe and recognized globally?",
            "instruction": " Acknowledge the explanation and ask about the global recognition and safety of traditional medicine.",
            "snippet": [],
            "out_of_knowledge": false
        },
        {
            "role": "Assistant",
            "generated_text": "Safety remains a paramount concern in all medical practices. In traditional medicine systems, various treatments, including herbal remedies, acupuncture, and homeopathy, are employed due to their perceived natural and safer alternatives to pharmaceutical products. However, it's crucial to recognize that these traditional products are not inherently risk-free and may pose health risks, especially when combined with other medications. To ensure safety, traditional medicine products and therapies must undergo rigorous testing and clinical trials to verify their quality, efficacy, and safety. The global utilization of traditional medicine is extensive, with reports from more than 100 countries indicating significant adoption. As of 2012, nearly half of the populations in several industrialized nations, and up to 80% in certain African regions, engage regularly in some form of traditional medicine, highlighting its widespread acceptance and use.",
            "instruction": "",
            "snippet": [
                {
                    "url": "https://www.who.int/news-room/questions-and-answers/item/traditional-medicine",
                    "language": "ENG",
                    "data": {
                        "type": "qa_pair",
                        "topic": "traditional medicine",
                        "title": "How widely is traditional medicine used?",
                        "content": "For centuries, traditional and complementary medicine (T&CM) has been an integral resource for health in households and communities. One hundred seventy countries reported on the use of traditional medicine, with acupuncture being the most common form of practice in 113 countries. Many developed countries have also begun recognizing and integrating traditional medicine into their healthcare systems.\n\n According to 2012 data, almost half the population in many industrialized countries now regularly uses some form of T&CM (United States, 42%; Australia, 48%; France, 49%; Canada, 70%); considerable use of some form of T&CM exists in many other countries, such as Chile (71%), Colombia (40%) and up to 80% in some African countries. "
                    },
                    "parallel_data": false,
                    "parallel_identifier": "traditional-medicine-qa2",
                    "unique_identifier": "traditional-medicine-qa2"
                },
                {
                    "url": "https://www.who.int/news-room/questions-and-answers/item/traditional-medicine",
                    "language": "ENG",
                    "data": {
                        "type": "qa_pair",
                        "topic": "traditional medicine",
                        "title": "Is traditional medicine safe?",
                        "content": "The first principle in medicine is to do no harm and safety is always a fundamental principle in the provision of any health-care treatment and procedures. WHO has consistently advocated for the integration into national health systems of traditional medicine practices and products that meet the standards of quality, safety and efficacy.\n\nHerbal remedies and treatments such as acupuncture and homeopathy are widely used in traditional medicine systems. Most are readily available and easy to use. Because many are considered natural, they are perceived to be safe and healthier than pharmaceutical substances. However, contrary to popular belief, traditional medicine products are not always safe and can have negative health consequences, particularly when used in combination with other medicines (see here) or when taken in high doses.\n\nUsers need to be better informed as to the actual benefits and properties of traditional forms of therapy and their potential hazards, and that they have access to the information that is reliable, clear and easily available. Improper use puts consumers at risk for potentially serious side effects as a result of allergies, drug interactions, contamination of the products with pesticides, heavy metals and other substances, or trauma inflicted by inexperienced or poorly trained practitioners.\n\nAny T&CM product or therapy should follow strict protocol and be subjected to tests and clinical trials for quality, efficacy and patient safety."
                    },
                    "parallel_data": false,
                    "parallel_identifier": "traditional-medicine-qa3",
                    "unique_identifier": "traditional-medicine-qa3"
                }
            ],
            "out_of_knowledge": false
        },
        {
            "role": "Patient",
            "generated_text": "How are the results of traditional medicine treatments compared to those of modern medicine?",
            "instruction": "Inquire about how the results of traditional medicine treatments compare to those of modern medicine.",
            "snippet": [],
            "out_of_knowledge": false
        },
        {
            "role": "Assistant",
            "generated_text": "That’s a great question, but I’m afraid I don’t have specific comparative data at hand. The effectiveness can vary widely depending on the condition, the type of traditional medicine used, and the individual. For accurate comparisons, it's best to look at specific studies or clinical trial results.",
            "instruction": "",
            "snippet": [],
            "out_of_knowledge": false
        },
        {
            "role": "Patient",
            "generated_text": "That helps a lot, thank you! Where can I get more detailed information?",
            "instruction": "Thank the assistant for the information and ask for resources to learn more about traditional medicine.",
            "snippet": [],
            "out_of_knowledge": false
        },
        {
            "role": "Assistant",
            "generated_text": "You’re welcome! For more detailed information, you should visit the WHO's official webpage on traditional medicine. They provide extensive details on their ongoing initiatives and global strategies.",
            "instruction": "",
            "snippet": [],
            "out_of_knowledge": false
        }
    ]
}
