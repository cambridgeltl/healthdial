import React from 'react';
import './index.css';
import { Button, Result, Layout, Typography, Descriptions } from 'antd';
import { ProfileOutlined } from '@ant-design/icons';
import {contact_name, contact_email} from "./configs";
import { useNavigate } from 'react-router-dom';

const { Paragraph, Text } = Typography;

const { Header, Content, Footer } = Layout;

const Welcome: React.FC = () => {
    const navigate = useNavigate();

    return(
    <Layout>
        <Header
            style={{
                backgroundColor:'#F5F5F5FF',
            }}
        >
        </Header>
        <Content className="site-layout">
            <Result
                icon={<ProfileOutlined />}
                title="Please Login or Register"
                extra={[
                    <Button key="login" onClick={ (e) => {
                        e.preventDefault()
                        navigate('/login')
                    }
                    }>
                        Login
                    </Button>,

                    <Button type="primary" key="register" onClick={ (e) => {
                        e.preventDefault();
                        navigate('/consent')
                    }
                    }>
                        Register
                    </Button>
                ]}
            >

                <div className="info">


                    <Paragraph>
                        <Text
                            strong
                            style={{
                                fontSize: 16,
                            }}
                        >
                            Welcome to our experimental study!
                            <br/>
                            <br/>
                            Here is a summary about this task.
                        </Text>
                    </Paragraph>

                    <Descriptions bordered>
                        <Descriptions.Item span={2} label="Contact">{contact_name} {contact_email}</Descriptions.Item>
                        <Descriptions.Item span={1} label="How long will it take">5 minutes per task</Descriptions.Item>
                    </Descriptions>

                    <br/>

                    <Paragraph>
                        <Text
                            strong
                            style={{
                                fontSize: 16,
                            }}
                        >

                            If you do not have an account, please click the Register button below to start.

                            1. You will find out what the experiment is about and what you will be asked to do.

                            2. You will also be asked to sign a consent form.

                            3. Then you will be headed to registration.
                            <br/>

                            <br/>

                            If you already have an account, please click the Login button above to start.

                        </Text>
                    </Paragraph>

                </div>


            </Result>

        </Content>
        <Footer style={{ textAlign: 'center', backgroundColor:'#F5F5F5FF' }}>Cambridge LTL ©2025</Footer>
    </Layout>
    )
}

export default Welcome;
