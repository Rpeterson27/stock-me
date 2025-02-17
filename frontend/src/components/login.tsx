import { StytchLogin } from "@stytch/react";
import { Products } from '@stytch/vanilla-js';
import { Container, Paper, Title } from "@mantine/core";
import styles from './login.module.css';

const Login = () => {
  return (
    <Container size="xs" className={styles.container}>
      <Paper shadow="md" p="xl" radius="md" className={styles.paper}>
        <Title order={2} ta="center" mb="xl">Welcome to StockMe</Title>
        <StytchLogin
          config={{
            products: [Products.oauth],
            oauthOptions: {
              providers: [{ 
                type: 'google',
                one_tap: true,
                position: 'floating'
              }],
              loginRedirectURL: window.location.origin + '/authenticate',
              signupRedirectURL: window.location.origin + '/authenticate'
            }
          }}
          styles={{
            container: {
              width: '100%'
            },
            buttons: {
              primary: {
                backgroundColor: '#4285f4',
                borderColor: '#4285f4',
                borderRadius: '4px',
                // fontSize: '16px',
                textColor: '#ffffff',
                // width: '100%',
                // marginBottom: '16px'
              }
            }
          }}
        />
      </Paper>
    </Container>
  );
};

export default Login;
