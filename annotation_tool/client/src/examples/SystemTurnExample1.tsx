import React, {useState} from 'react';
import {Row, Col, Card, Divider, Form, Input, Steps, Avatar, message, theme, Button, Result, Tooltip} from 'antd';
import {colour_array, system_colour, user_colour} from "../configs";

import {KnowledgeSnippetType} from '../types/taskTypes';
import {CustomerServiceOutlined, SmileOutlined, UserOutlined} from "@ant-design/icons";
import { AudioRecorder } from 'react-audio-voice-recorder';
import KnowledgeSnippetList from "../KnowledgeSnippetList";

const { TextArea } = Input;


interface SystemTurnProps {
    generated_system_utterance: string;
    snippet_list: KnowledgeSnippetType[];
    turn_idx : number;
    is_annotation : boolean
}

const SystemTurnExample1: React.FC<SystemTurnProps> = ({generated_system_utterance,snippet_list, turn_idx, is_annotation}) => {

    const [messageApi, contextHolder] = message.useMessage();
    const { token } = theme.useToken();
    const this_colour_array = is_annotation ? user_colour : system_colour;

    const contentStyle: React.CSSProperties = {
        height: 200,
        textAlign: 'center',
        display: 'flex',         // Set display to flex
        justifyContent: 'center', // Center horizontally
        alignItems: 'center',     // Center vertically
        color: token.colorTextTertiary,
        backgroundColor: token.colorFillAlter,
        borderRadius: token.borderRadiusLG,
        border: `1px dashed ${token.colorBorder}`,
        marginTop: 16,
    };



    return (
        <div>

            {contextHolder}
            <Divider plain orientation="left">
                System Turn {turn_idx}

            </Divider>
            <Row style={{background: this_colour_array[1], padding: '10px'}} gutter={6}>
                <Col span={12}>
                    <Row>
                        <Col span={2} >
                            <Avatar
                                style={{ backgroundColor: this_colour_array[0]}}
                                icon={<CustomerServiceOutlined/>}
                            />
                        </Col>
                        <Col span={20} >
                            <Tooltip title="Ensure you also read the system message to maintain coherence and relevance within the context." visible={true}  placement="top" >
                                <TextArea value={generated_system_utterance} autoSize />
                            </Tooltip>

                        </Col>

                    </Row>

                </Col>

                <Col span={12}>
                    {/*<Tooltip title="These are the knowledge snippets that support this utterance. In this task, you do not need to read these snippets." visible={true}  placement="left" >*/}
                    {/*    <KnowledgeSnippetList snippet_list={snippet_list}/>*/}
                    {/*</Tooltip>*/}
                </Col>
            </Row>

        </div>

    );
};

export default SystemTurnExample1;
