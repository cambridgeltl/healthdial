import React from "react";
import {message, Input, Button, Collapse, Form, Layout, Rate, Timeline, Radio} from 'antd';
import {serverUrl} from "./configs";
import {contact_name, contact_email, contact_address} from "./configs";
import {NavigateFunction, useNavigate} from "react-router-dom";
// import Chatbox from "./Chatbox";
import { useEffect, useState} from "react";
import parse from "html-react-parser";
import useToken from "./service/TokenService";
import VoiceChatBox from "./Chatbox";

const {Header, Content, Footer} = Layout;

const rateDescriptions = ['Very Dissatisfied', 'Dissatisfied', 'Slightly Dissatisfied', 'Neutral', 'Slightly Satisfied', 'Satisfied', 'Very Satisfied'];


// Updated Type definition (extended to match form)
type EvaluateFieldType = {
    usefulness: number;
    easeOfUse: number;
    outputQuality: number;
    intentionToUse: number;
    overall: number;
    goal: number;
    trust: number;
    preferredTool: string;
    preferredReason?: string;
    whoOverall: number;
    taskCompletion: number;
    feedback?: string;
};

// Function to handle form submission on evaluation completion
function onFinish(
    values: EvaluateFieldType,
    navigate: NavigateFunction,
    token: string | null
) {
    const payload = {
        usefulness: values.usefulness,
        easeOfUse: values.easeOfUse,
        outputQuality: values.outputQuality,
        intentionToUse: values.intentionToUse,
        overall: values.overall,
        goal: values.goal,
        trust: values.trust,
        preferredTool: values.preferredTool,
        preferredReason: values.preferredReason || "",
        whoOverall: values.whoOverall,
        taskCompletion: values.taskCompletion,
        feedback: values.feedback || "",
    };

    fetch(serverUrl + '/api/save_result', {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + token
        },
        body: JSON.stringify(payload)
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(json => {
            if (!json.success) {
                message.error(json.msg || 'Submission failed. Please try again.');
            } else {
                message.success('Thank you! Your feedback has been successfully submitted.');
                navigate('/result');
            }
        })
        .catch(error => {
            console.error("Submission error:", error);
            message.error('An error occurred while submitting your feedback. Please try again.');
        });
}


// Function to handle form submission failure
function onFinishFailed(){
    message.error('Please complete the following evaluation questions!');
}

// Function to fetch the task for the user
function getTask(setUserGoal: React.Dispatch<React.SetStateAction<string[]>>, token: string | null) {
    if (!token) {
        console.error("No token available for authorization");
        return;
    }


    fetch(serverUrl+'/api/get_task', { // Update with your server URL
        method: 'GET',
        headers: {
            'Authorization': 'Bearer ' + token,
            'Content-Type': 'application/json'
        }
    })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success && data.task) {
                setUserGoal(data.task.task); // Assuming the task is an array of strings
            } else {
                console.error('Failed to fetch task data:', data.msg);
            }
        })
        .catch(error => {
            console.error('Error fetching task data:', error);
        });
}



const Assignment: React.FC = () => {
    const navigate = useNavigate();
    const [userGoal, setUserGoal] = useState<string[]>([]);
    const { token } = useToken();


    useEffect(() =>{
        getTask(setUserGoal, token)
    }, [token])

    return(

            <Layout>
                <Header
                    style={{
                        backgroundColor:'#F5F5F5FF',
                        padding: 0,
                    }}
                >
                    <div style={{display: 'flex', justifyContent: 'center',    alignItems: 'center'}}>
                        <b>
                            Healthcare Dialogue Collection Experiment
                        </b>
                    </div>

                </Header>

                <Content className="site-layout">
                    <div>
                        <Collapse defaultActiveKey={['1','2','3','4']}>
                            <Collapse.Panel header="Contact" key="1" >
                                <p style={{"fontSize": 15, 'whiteSpace': 'pre-line'}}>
                                    {contact_name}
                                    <br/>
                                    {contact_address}
                                    <br/>
                                    {contact_email}
                                </p>
                            </Collapse.Panel>

                            <Collapse.Panel header="Step 1: Instruction" key="1">
                                <p style={{ fontSize: 15, whiteSpace: 'pre-line' }}>
                                    In this task, you will explore two different tools for finding health-related information:
                                </p>

                                <ul style={{ fontSize: 15 }}>
                                    <li>The official <b>WHO Website</b></li>
                                    <li>A <b>Dialogue System</b> that allows you to ask health-related questions through conversation</li>
                                </ul>

                                <p style={{ fontSize: 15, whiteSpace: 'pre-line' }}>
                                    First, we will ask you to visit the WHO website to search for information.
                                    After that, you will talk with our assistant by typing your questions or requests in a chat-like format.
                                </p>

                                <p style={{ fontSize: 15, whiteSpace: 'pre-line' }}>
                                    You will be given a <b>hypothetical health-related scenario</b> (e.g., back pain, vaccine concerns, or a skin condition).
                                    Please try to find useful and trustworthy information on both platforms about your assigned scenario.
                                </p>

                                <br/>
                                <br/>

                                <Timeline>
                                    {
                                        userGoal.map((goal, index) => (
                                            <Timeline.Item key = {index}>
                                                {parse(goal)}
                                            </Timeline.Item>
                                        ))
                                    }
                                </Timeline>

                                <p style={{ fontSize: 15, whiteSpace: 'pre-line' }}>
                                    Imagine it’s a real situation you or someone you care about is facing.
                                    Search naturally — just as you would if you were genuinely trying to solve a health concern.
                                </p>

                                <p style={{ fontSize: 15, whiteSpace: 'pre-line' }}>
                                    At the end of the task, you will be asked to fill out a short questionnaire comparing your experience with both systems.
                                    There are no right or wrong answers — we are simply interested in your opinion.
                                </p>

                            </Collapse.Panel>



                            <Collapse.Panel header="Step 2: Visiting WHO Website" key="2">
                                <p style={{ fontSize: 15, whiteSpace: 'pre-line' }}>
                                    Please visit the official WHO website to look for health information related to your assigned scenario.
                                    Try to find useful and trustworthy answers — just as you would in a real-life situation.
                                    You can browse articles, use the search bar, and explore the relevant pages.
                                </p>

                                <p style={{ fontSize: 15, whiteSpace: 'pre-line' }}>
                                    When you're finished exploring, return to this page to move on to the chatbot.
                                </p>

                                <Button type="link" href="https://www.who.int" target="_blank">
                                    Open WHO Website in New Tab ↗
                                </Button>
                            </Collapse.Panel>


                            <Collapse.Panel header="Step 3: Chat with Chatbot" key="3">
                                <p style={{ fontSize: 15, whiteSpace: 'pre-line' }}>
                                    Now it's time to chat with our health assistant chatbot!
                                    You can ask questions, explain your situation, and follow up naturally — just like talking to a doctor or online support service.
                                </p>

                                <p style={{ fontSize: 15, whiteSpace: 'pre-line' }}>
                                    The chatbot supports both <b>text</b> and <b>voice</b>.
                                    You can type your questions, or speak directly by clicking the <b>microphone icon in the bottom-right corner</b>.
                                </p>

                                <p style={{ fontSize: 15, whiteSpace: 'pre-line' }}>
                                    Try to use the chatbot to find the same kind of information you searched for on the WHO website.
                                    Feel free to ask in your own words and follow up naturally if something is unclear.
                                </p>

                                <p style={{ fontSize: 15, whiteSpace: 'pre-line' }}>
                                    After you finish the conversation, you’ll be asked to complete a short questionnaire to share your experience.
                                </p>

                                <div style={{ height: '600px', padding: '20px', border: '1px solid #f0f0f0', borderRadius: '8px', overflowY: 'auto' }}>
                                    <VoiceChatBox />
                                </div>
                            </Collapse.Panel>


                            <Collapse.Panel header="Step 4: Evaluate and Compare" key="4">
                                <p style={{ fontSize: 15, whiteSpace: 'pre-line' }}>
                                    Please evaluate your experience using the dialogue system compared to the WHO website.
                                    There are no right or wrong answers — we’re simply interested in your honest impressions.
                                    Your feedback will help us improve the system.
                                </p>

                                <p style={{ fontSize: 13, marginBottom: 24 }}>
                                    For the following questions, please rate from 1 to 7:
                                    <br />
                                    <b>1 = Strongly Disagree  4 = Neutral  7 = Strongly Agree</b>
                                </p>
                                <Form
                                    name="evaluation"
                                    layout="vertical"
                                    onFinish={(x) => onFinish(x, navigate, token)}
                                    onFinishFailed={onFinishFailed}
                                    autoComplete="off"
                                    initialValues={{ feedback: "" }}
                                >


                                    {/* Perceived Usefulness */}
                                    <Form.Item label="1. The dialogue system helped me understand health information better than the WHO website." name="usefulness" rules={[{ required: true }]}>
                                        <Rate count={7} />
                                    </Form.Item>

                                    {/* Ease of Use */}
                                    <Form.Item label="2. The dialogue system was easier to use than the WHO website." name="easeOfUse" rules={[{ required: true }]}>
                                        <Rate count={7} />
                                    </Form.Item>

                                    {/* Output Quality */}
                                    <Form.Item label="3. The dialogue system gave me more useful answers than the WHO website." name="outputQuality" rules={[{ required: true }]}>
                                        <Rate count={7} />
                                    </Form.Item>

                                    {/* Behavioural Intention */}
                                    <Form.Item label="4. I would prefer using the dialogue system over the WHO website in the future." name="intentionToUse" rules={[{ required: true }]}>
                                        <Rate count={7} />
                                    </Form.Item>
                                    <Form.Item label="5. Overall satisfaction with the dialogue system?" name="overall" rules={[{ required: true }]}>
                                        <Rate count={7} tooltips={rateDescriptions} />
                                    </Form.Item>


                                    {/* Goal Achievement */}
                                    <Form.Item label="6. Did the system help you find the answers?" name="goal" rules={[{ required: true }]}>
                                        <Radio.Group>
                                            <Radio value={1}>Yes</Radio>
                                            <Radio value={2}>Partially</Radio>
                                            <Radio value={3}>No</Radio>
                                        </Radio.Group>
                                    </Form.Item>

                                    {/* Trust */}
                                    <Form.Item label="7. I trust the information provided by the dialogue system more than the WHO website." name="trust" rules={[{ required: true }]}>
                                        <Rate count={7} />
                                    </Form.Item>

                                    {/* Preferred Tool */}
                                    <Form.Item label="8. If you had a health concern, which tool would you use first?" name="preferredTool" rules={[{ required: true }]}>
                                        <Radio.Group>
                                            <Radio value="dialogue">Dialogue System</Radio>
                                            <Radio value="who">WHO Website</Radio>
                                            <Radio value="depends">It depends</Radio>
                                        </Radio.Group>
                                    </Form.Item>

                                    {/* Reason */}
                                    <Form.Item label="9. Why did you choose that option?" name="preferredReason">
                                        <Input.TextArea rows={2}/>
                                    </Form.Item>

                                    <Form.Item label="10. Overall, how satisfied were you with the WHO website?" name="whoOverall" rules={[{ required: true }]}>
                                        <Rate count={7} tooltips={rateDescriptions} />
                                    </Form.Item>


                                    {/* Task Completion */}
                                    <Form.Item label="11. How much of the needed information did you find?" name="taskCompletion" rules={[{ required: true }]}>
                                        <Radio.Group>
                                            <Radio value={1}>All of it</Radio>
                                            <Radio value={2}>Most of it</Radio>
                                            <Radio value={3}>Some of it</Radio>
                                            <Radio value={4}>Very little or none</Radio>
                                        </Radio.Group>
                                    </Form.Item>

                                    {/* Feedback */}
                                    <Form.Item label="12. Any additional feedback or suggestions?" name="feedback">
                                        <Input.TextArea rows={3}/>
                                    </Form.Item>

                                    <Form.Item wrapperCol={{ span: 24 }}>
                                        <Button type="primary" htmlType="submit">Submit</Button>
                                    </Form.Item>
                                </Form>

                            </Collapse.Panel>


                        </Collapse>

                    </div>

                </Content>
                <Footer style={{ textAlign: 'center', backgroundColor:'#F5F5F5FF' }}>Cambridge LTL ©2025</Footer>
            </Layout>
        )
}


export default Assignment;
