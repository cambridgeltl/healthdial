import React from "react";
import {
    message,
    Input,
    Button,
    Collapse,
    Layout,
    Radio,
    Select,
    Divider,
    Row,
    Col, Card, Alert, Tooltip, Switch, Space, Avatar, Tag, Timeline
} from 'antd';


import {serverUrl, experiment_title, user_colour, system_colour} from "./configs";
import {target_language, contact_name, contact_email, contact_address, exampleTask} from "./configs";
import {NavigateFunction, useNavigate} from "react-router-dom";
import UserTurn from "./UserTurn";
import SystemTurn from "./SystemTurn";
import {AudioOutlined, CustomerServiceOutlined, SaveOutlined, UserOutlined} from "@ant-design/icons";
import {TaskType} from "./types/taskTypes";
import UserTurnExample1 from "./examples/UserTurnExample1";
import SystemTurnExample1 from "./examples/SystemTurnExample1";
import TaskCard from "./TaskCard";
import {AudioRecorder} from "react-audio-voice-recorder";
import TaskCardExample1 from "./examples/TaskCardExample1";
import TaskCardExample2 from "./examples/TaskCardExample2";
const { TextArea } = Input;

const {Header, Content, Footer} = Layout;



const initTask: TaskType = exampleTask

const Instruction: React.FC = () => {
    const navigate = useNavigate();

    return (

        <Layout>
            <Header
                style={{
                    backgroundColor: '#F5F5F5FF',
                    padding: 0,
                }}
            >
                <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center'}}>
                    <b>
                        {experiment_title}
                    </b>
                </div>

            </Header>

            <Content className="site-layout">
                <div>
                    <Collapse defaultActiveKey={['1', '2', '3', '4', '5']}>

                        <Collapse.Panel header="Contact" key="1">
                            <p style={{"fontSize": 15, 'whiteSpace': 'pre-line'}}>
                                {contact_name}
                                <br/>
                                {contact_address}
                                <br/>
                                {contact_email}
                            </p>
                        </Collapse.Panel>


                        <Collapse.Panel header="Instruction" key="2">

                            <div>

                            Imagine you are speaking with an AI health assistant over the phone and you want to inquire about health topics for professional advice.


                            <br/>
                            <br/>

                            For example, you have come across the concept of { }
                            <Tag bordered={false} color="processing">
                                traditional medicine
                            </Tag>
                            and are eager to learn more about it. You initiate a discussion on this topic, and the AI assistant provides you with detailed information.

                            <br/>
                            <br/>


                            In this experimental study, you will take on the role of a patient or client

                            <Avatar
                                style={{ backgroundColor: user_colour[0], marginLeft: '5px'}}
                                icon={<UserOutlined />}
                                size="small"
                            />

                            . Picture yourself engaging in a real conversation with a doctor at a hospital, clinic, or through a health information hotline. The goal is to simulate natural conversations that might occur between two native speakers of {target_language}.

                            <div>
                                <h3>As a participant, your task involves:</h3>


                                        <b>Understanding the Context:</b>
                                        <p>Read through the prompts on the left-hand side and understand the context of the conversation.</p>


                                        <b>Dialogue Creation:</b>
                                        <p>Then, you will be asked to complete the task card on the right hand side.</p>

                                        <ul>
                                            <li>Step 1: create a natural and coherent dialogue utterance as if spoken.</li>
                                            <li>Step 2: transcribe the spoken utterance into text.</li>
                                        </ul>
                                        <p>Continue creating and transcribing dialogue until the all the task cards are complete.</p>



                            </div>


                        </div>
                        </Collapse.Panel>




                        <Collapse.Panel header="How to Use this Tool " key="3">

                            In the following example, you will see a conversation turn between a user
                            <Avatar
                                style={{ backgroundColor: user_colour[0], margin: '5px'}}
                                icon={<UserOutlined />}
                                size="small"
                            />

                            (this is your role) and an AI assistant
                            <Avatar
                                style={{ backgroundColor: system_colour[0], marginLeft: '5px'}}
                                icon={<CustomerServiceOutlined/>}
                                size="small"
                            />

                            . The primary task involves annotating user utterances to ensure they are contextually appropriate and coherent. You will encounter a dialogue turn setup as follows:





                            <UserTurnExample1 generated_user_utterance={initTask.utterance[1].instruction} is_annotation={true} turn_idx={1} />
                            <SystemTurnExample1 generated_system_utterance={initTask.utterance[2].generated_text} snippet_list={initTask.utterance[2].snippet} is_annotation={false} turn_idx={1} />

                            <br/>

                            For your task, you will see a series of dialogue turns similar to the above example. Your specific task is to <b>annotate each user utterance</b>, ensuring it <b>aligns well with the surrounding context</b> provided by both preceding and succeeding system utterances. System utterances serve as a contextual guide. While they are not the focus of your annotation, they help you understand the dialogue's flow and ensure your annotations are contextually accurate.

                            <h3>Now, we provide further instructions on how to use the task card for effective annotation.</h3>

                            <p>The following is an example task card. You may notice that the  <Button size="small"
                                                                                                       type="primary"
                                                                                                       disabled={true}>
                                Next
                            </Button> button is initially disabled. This is a built-in feature to guide you through the task systematically. The "Next" button will remain disabled until you complete Step 1, which involves recording audio.</p>


                            <p>Now please click the audio recording <AudioOutlined /> button and start a recording. Once you finish your recording, please click the <SaveOutlined /> button and save the audio. Upon successful completion of the audio recording, the "Next" button will be enabled, allowing you to proceed.</p>

                            <TaskCard style={{width: 600}} before_login={true}/>


                            <p>
                                After completing the recording, proceed to Step 2, where you will listen to the audio you just recorded and transcribe it into text. You will be provided an automatically generated transcriptions to start with. You can edit the transcription as needed. If the recorded audio is unclear, you can click the <Button size="small" style={{ margin: '0 8px' }}>
                                Previous
                            </Button> button to go back and record a new one.
                            </p>

                            <TaskCardExample1 style={{width: 600}}/>


                            <p>
                                After completing Step 2, click the "Next" button to proceed. It may take a few seconds to process your submission. Once the submission is validated and recorded, you will be shown a confirmation page.
                                Great, you have completed this task card!
                            </p>

                            <TaskCardExample2 style={{width: 600}}/>


                            <p>
                                Now that you understand your task and how to use the task card, let me show you an example of the type of dialogue you will encounter during this experimental study.

                            </p>
                            <Alert message="You will see similar dialogues throughout this experimental study. For each dialogue, you must complete all task cards." type="info" />



                        </Collapse.Panel>

                        <Collapse.Panel header="Example Dialogue" key="4">
                            <Alert message="The example below is provided for your reference and understanding of the task instructions. This is not the task you are required to complete. To begin the qualification task, please click 'Submit' and proceed." type="warning" />
                            <Alert message={"This example is in English. For your task, you are required to speak in "+ target_language +". You are encouraged to use your local dialect while completing the task."} type="info" />


                            <SystemTurn generated_system_utterance={initTask.utterance[0].generated_text} snippet_list={initTask.utterance[0].snippet} is_annotation={false} turn_idx={0} />


                            <UserTurn generated_user_utterance={initTask.utterance[1].instruction} is_annotation={true} turn_idx={1} before_login={true}/>
                            <SystemTurn generated_system_utterance={initTask.utterance[2].generated_text} snippet_list={initTask.utterance[2].snippet} is_annotation={false} turn_idx={1} />


                            <UserTurn generated_user_utterance={initTask.utterance[3].instruction} is_annotation={true} turn_idx={2} before_login={true} />
                            <SystemTurn generated_system_utterance={initTask.utterance[4].generated_text} snippet_list={initTask.utterance[4].snippet} is_annotation={false} turn_idx={2} />


                            <UserTurn generated_user_utterance={initTask.utterance[5].instruction} is_annotation={true} turn_idx={3} before_login={true} />
                            <SystemTurn generated_system_utterance={initTask.utterance[6].generated_text} snippet_list={initTask.utterance[6].snippet} is_annotation={false} turn_idx={3} />


                            <UserTurn generated_user_utterance={initTask.utterance[7].instruction} is_annotation={true} turn_idx={4} before_login={true}/>
                            <SystemTurn generated_system_utterance={initTask.utterance[8].generated_text} snippet_list={initTask.utterance[8].snippet} is_annotation={false} turn_idx={4} />

                        </Collapse.Panel>


                        <Collapse.Panel header="Before You Proceed" key="5">

                            <Alert message="Please make sure you fully understand your task and how to use this web annotation tool. If anything is unclear, feel free to contact me via email." type="info" />
                            <div style={{ display: 'flex', justifyContent: 'center', marginTop: 20 }}>
                                <Button type="primary" onClick={() => navigate("/consent")}>
                                    Submit
                                </Button>
                            </div>
                        </Collapse.Panel>




                    </Collapse>
                </div>

            </Content>
            <Footer style={{textAlign: 'center', backgroundColor: '#F5F5F5FF'}}>Cambridge LTL ©2024</Footer>
        </Layout>
    );
}


export default Instruction;
