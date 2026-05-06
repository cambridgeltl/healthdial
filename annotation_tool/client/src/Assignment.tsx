import React from "react";
import {
    message,
    Input,
    Button,
    Collapse,
    Form,
    Layout,
    Avatar, Alert
} from 'antd';

import {serverUrl, experiment_title, user_colour} from "./configs";
import {target_language, contact_name, contact_email, contact_address, exampleTask, colour_array} from "./configs";
import {NavigateFunction, useNavigate} from "react-router-dom";
import { useEffect, useState, createContext, useRef} from "react";
import useToken from "./service/TokenService";
import {TaskType, UtteranceType, SubmissionDicType, SubmissionItem} from './types/taskTypes';
import {UserOutlined} from "@ant-design/icons";
import UserTurn from "./UserTurn";
import SystemTurn from "./SystemTurn";
import axios from "axios";

const { TextArea } = Input;

const {Header, Content, Footer} = Layout;


const initTask: TaskType = exampleTask


function onFinish (values: SubmissionDicType, navigate: NavigateFunction, token: string | null, task: TaskType, startTime: Date | null){


    console.log("submit")
    console.log('Received values of form: ', values);
    console.log("body")

    if (!startTime) {
        console.error("Start time is missing!");
        message.error("An error occurred. Please refresh the page and try again.");
        return;
    }

    // const submission_list: SubmissionItem[] = task.utterance
    //     .map((turn, index) => ({
    //     blob_data: values[`blobData_${index}`] as Blob | null,
    //     transcription: values[`transcription_${index}`] as string,
    //     asr: values[`asrResult_${index}`] as string,
    // }));


    const submission_list: SubmissionItem[] = task.utterance.reduce((list, turn, index) => {
        if (turn.role.toLowerCase() === "patient") {
            list.push({
                blob_data: values[`blobData_${index}`] as Blob | null,
                transcription: values[`transcription_${index}`] as string,
                asr: values[`asrResult_${index}`] as string,
            });
        }
        return list;
    }, [] as SubmissionItem[]);


    console.log("submission_list")
    console.log(submission_list)

    const formData = new FormData();

    for (let i = 0; i < submission_list.length; i++) {
        const blob_data = submission_list[i].blob_data;

        if (blob_data != null) {
            const blob = new Blob([blob_data], { type: 'audio/wav' });
            formData.append('audio', blob, task.task_id + '_' + i + '.wav');
            formData.append('transcription', submission_list[i].transcription);
            formData.append('asr_result', submission_list[i].asr);
        } else {
            throw new Error("Please upload an audio file");
        }
    }

    formData.append('task_id', task.task_id);
    formData.append('language', target_language);
    formData.append('start_time', startTime.toISOString());


    // console.log(submission_list)
    console.log(task.task_id)
    console.log("formData")
    console.log(formData)

    fetch(serverUrl+'/api/save_result', {
        method: 'POST',
        headers: {
            'Authorization': 'Bearer ' + token
        },
        body: formData
    })
        .then(function (response) {
            console.log(response);
            return response.json();
        })
        .then(function (json) {
            console.log(json)
          if(json.success === false){
                message.error(json.msg);
          }
          else
          {
              navigate('/result');
          }
        });
}


function onFinishFailed(errorInfo:any){
    console.log('Failed:', errorInfo);
    message.error('Please complete all questions!');
}




function getTask(setTask: React.Dispatch<React.SetStateAction<TaskType>>,  navigate: NavigateFunction, token: string | null, setCompletedNumber: React.Dispatch<React.SetStateAction<number>>, setToken: (token: string | null) => void) {
    if (!token) {
        message.error("This webpage has expired. Please close this page and log in again.");
        console.error("No token available for authorisation.");
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
            if (response.status === 401) {
                throw new Error("Unauthorised - Token expired or invalid. Please close the window and try again.");
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success && data.task) {

                console.log("Fetched task:", data.task.task);
                setTask(data.task.task);

                if (data.access_token && typeof data.access_token === "string") {
                    setToken(data.access_token);
                }
                const completedTasks = Math.max(0, (data.task.completed_tasks ?? 1) - 1);
                setCompletedNumber(completedTasks)
                console.log("completedTasks", completedTasks)
                // if (completedTasks > 0) {
                //     message.info(`You have completed ${completedTasks} tasks so far. Keep going!`);
                // }

            } else {
                console.error('Failed to fetch task data:', data.msg);
                if(data.msg === "task all done"){
                    navigate("/done")
                }
            }
        })
        .catch(error => {
            message.error("Failed to fetch task data. Please refresh the page and try again.");

            console.error("Error fetching task data:", error);

        });
}


const Assignment: React.FC = () => {
    const navigate = useNavigate();
    const [task, setTask] = useState<TaskType>(initTask);
    const [startTime, setStartTime] = useState<Date | null>(null);
    const [completedNumber, setCompletedNumber] = useState<number>(0);

    const { token, removeToken, setToken, getUserRole, getUserPermissions } = useToken();
    const [hasAccessControl, setHasAccessControl] = useState<boolean>(false);
    const [form] = Form.useForm();


    // Function to fetch access control status
    const fetchAccessControlStatus = () => {
        if (!token) {
            console.error("No token available for authorization");
            return;
        }

        console.log("fetchAccessControlStatus")

        fetch(serverUrl+'/api/get_access_control', {
            method: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token,
                'Content-Type': 'application/json'
            }
        })
            .then(response => {
                console.log("response")
                console.log(response)
                console.log("!response.ok")
                console.log(!response.ok)
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {

                console.log("data")
                console.log(data)

                if (data.success) {
                    console.log("setHasAccessControl data")
                    console.log(data)
                    setHasAccessControl(data.access_control_enabled);
                } else {
                    console.error('Failed to fetch access control status:', data.msg);
                }
            })
            .catch(error => {
                console.error('Error fetching access control status:', error);
            });
    };

    useEffect(() => {
        fetchAccessControlStatus();
    }, [fetchAccessControlStatus, token]);

    useEffect(() => {
        const now = new Date();
        setStartTime(now);
    }, []);

    useEffect(() => {
        const userPermissions = getUserPermissions();
        console.log("userPermissions")
        console.log(userPermissions)

        if(hasAccessControl){
            if (!userPermissions.includes("visit_task_page_with_access_control")) {
                message.warning('Access Denied. Redirecting to the home page. For questions, please contact the task organiser.');
                navigate('/'); // Redirect to the root page
            }
        }else{
            if (!userPermissions.includes("visit_task_page")) {
                message.warning('Access Denied. Redirecting to the home page. For questions, please contact the task organiser.');
                navigate('/'); // Redirect to the root page
            }
        }

    }, [hasAccessControl, getUserPermissions, navigate]);

    useEffect(() =>{
        getTask(setTask, navigate, token, setCompletedNumber, setToken)
    }, [])

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
                    <Collapse defaultActiveKey={['1', '2', '3']}>

                        <Collapse.Panel header="Contact" key="1">
                            <p style={{"fontSize": 15, 'whiteSpace': 'pre-line'}}>
                                {contact_name}
                                <br/>
                                {contact_address}
                                <br/>
                                {contact_email}
                            </p>
                            {completedNumber > 0 && (
                                <div>
                                    <Alert message={"You have completed " + completedNumber +  " tasks so far. Keep going!"} type="info" />

                                </div>
                            )}
                        </Collapse.Panel>


                        <Collapse.Panel header="Instruction" key="2">


                            Imagine you are speaking with an AI health assistant over the phone and you want to inquire about health topics for professional advice.

                            <br/>
                            <br/>


                            In this experimental study, you will take on the role of a patient or client

                            <Avatar
                                style={{ backgroundColor: user_colour[0], marginLeft: '5px'}}
                                icon={<UserOutlined />}
                                size="small"
                            />

                            . Picture yourself engaging in a real conversation with a doctor at a hospital, clinic, or through a healthcare information hotline. The goal is to simulate natural conversations that might occur between two native speakers of {target_language}.


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
                            <div>
                                <Alert message="Please note that the following dialogues may contain biases, such as unjustified associations between diseases and the names of countries. This is a known limitation of current language technologies. The release of this dataset will help researchers identify and mitigate such biases in the future." type="warning" />
                            </div>


                        </Collapse.Panel>

                        <Collapse.Panel header="Your Tasks" key="3">
                            <Alert message={"Please complete the following task in " + target_language +  ". You are encouraged to use your local dialect while completing the task."} type="info" />

                            <Form
                                name="annotation_form"
                                onFinish={(x) => onFinish(x, navigate, token, task, startTime)}
                                onFinishFailed={onFinishFailed}
                                autoComplete="off"
                                form={form}

                                initialValues={{
                                }}
                            >
                                <div>

                                    {task?.task_id === "ENG_EXAMPLE_1" && (
                                        <Alert message={"Please do not work on the following task. Your login details have expired. Please close this webpage and login again."} type="error" />
                                    )}

                                    {(task.utterance).map((dialogue_turn, turn_index) => (

                                            <div key={"turn" + turn_index}>
                                                {dialogue_turn.role.toLowerCase() === "assistant" &&
                                                    <SystemTurn
                                                        generated_system_utterance={dialogue_turn.generated_text}
                                                        snippet_list={dialogue_turn.snippet} is_annotation={false}
                                                        turn_idx={turn_index}/>
                                                }
                                                {dialogue_turn.role.toLowerCase() === "patient" &&
                                                    <UserTurn generated_user_utterance={dialogue_turn.instruction}
                                                              is_annotation={true} turn_idx={turn_index}
                                                              task_id={task.task_id} form={form}/>
                                                }
                                            </div>
                                        ))
                                        }

                                </div>


                                <Form.Item>

                                    <div style={{ display: 'flex', justifyContent: 'center', marginTop: 20 }}>
                                        <Button type="primary" htmlType="submit">
                                            Submit
                                        </Button>

                                    </div>


                                </Form.Item>
                            </Form>
                        </Collapse.Panel>
                    </Collapse>
                </div>

            </Content>
            <Footer style={{textAlign: 'center', backgroundColor: '#F5F5F5FF'}}>Cambridge LTL ©2024</Footer>
        </Layout>
    );
}


export default Assignment;
