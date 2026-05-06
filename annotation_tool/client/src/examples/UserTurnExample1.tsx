import React, {useState} from 'react';
import {Row, Col, Card, Divider, Form, Input, Steps, Avatar, message, theme, Button, Result, Tooltip} from 'antd';
import {colour_array, system_colour, user_colour} from "../configs";

import {KnowledgeSnippetType} from '../types/taskTypes';
import {SmileOutlined, UserOutlined} from "@ant-design/icons";
import { AudioRecorder } from 'react-audio-voice-recorder';
import TaskCard from "../TaskCard";

const { TextArea } = Input;


interface UserTurnProps {
    generated_user_utterance: string;
    turn_idx : number;
    is_annotation : boolean
}



const UserTurnExample1: React.FC<UserTurnProps> = ({generated_user_utterance, turn_idx, is_annotation}) => {

    const this_colour_array = is_annotation ? user_colour : system_colour;

    return (
        <div>

            <Divider plain orientation="left">
                User Turn {turn_idx}

            </Divider>
            <Row style={{background: this_colour_array[1], padding: '10px'}} gutter={6}>
                <Col span={12}>
                    <Row>
                        <Col span={2} >
                            <Avatar
                                style={{ backgroundColor: this_colour_array[0]}}
                                icon={<UserOutlined />}
                            />
                        </Col>
                        <Col span={20} >
                            <Tooltip title="This is the prompt you have to follow. Your task is to create natural and coherent sentences that convey the same meaning as the given prompt, maintaining a realistic conversational tone." visible={true}  placement="bottom" >
                                <TextArea value={generated_user_utterance} autoSize />
                            </Tooltip>
                        </Col>


                    </Row>

                </Col>

                <Col span={12}>

                    <Tooltip title="This is the task card to complete." visible={true}  placement="left" >
                        <TaskCard turn_id={-1} task_id={"example"} before_login={true}/>
                    </Tooltip>

                </Col>


            </Row>

        </div>

    );
};

export default UserTurnExample1;
