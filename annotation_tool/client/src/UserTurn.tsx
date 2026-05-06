import React, {useState} from 'react';
import {Row, Col, Card, Divider, Form, Input, Steps, Avatar, message, theme, Button, Result} from 'antd';
import {colour_array, system_colour, user_colour} from "./configs";

import {KnowledgeSnippetType} from './types/taskTypes';
import {SmileOutlined, UserOutlined} from "@ant-design/icons";
import { AudioRecorder } from 'react-audio-voice-recorder';
import TaskCard from "./TaskCard";

const { TextArea } = Input;


interface UserTurnProps {
    generated_user_utterance: string;
    turn_idx : number;
    task_id? : string;
    is_annotation : boolean;
    form?: any;
    before_login?: boolean;

}


const UserTurn: React.FC<UserTurnProps> = ({generated_user_utterance, turn_idx, is_annotation, task_id, form, before_login=false}) => {

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
                            <TextArea value={generated_user_utterance} autoSize />
                        </Col>


                    </Row>

                </Col>

                <Col span={12}>
                    <TaskCard turn_id={turn_idx} task_id={task_id} form={form} before_login={before_login}/>
                </Col>


            </Row>

        </div>

    );
};

export default UserTurn;
