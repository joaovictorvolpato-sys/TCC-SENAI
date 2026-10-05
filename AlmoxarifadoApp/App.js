import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  Image,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StatusBar,
} from 'react-native';

// Troque pelo endereço do seu servidor (o mesmo que recebia o POST em "/")
// No iPhone, "localhost" não funciona: use o IP da máquina, ex: http://192.168.0.10:5000/
const URL_LOGIN = 'http://192.168.56.1:5000/';

export default function Login() {
  const [usuario, setUsuario] = useState('');
  const [senha, setSenha] = useState('');
  const [mostrarSenha, setMostrarSenha] = useState(false);

  // Equivale ao toggleSenha() do HTML
  function toggleSenha() {
    setMostrarSenha(!mostrarSenha);
  }

  // Equivale ao <form action="/" method="POST">
  async function entrar() {
    try {
      const corpo = new URLSearchParams({
        username: usuario,
        password: senha,
      }).toString();

      const resposta = await fetch(URL_LOGIN, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: corpo,
      });

      if (resposta.ok) {
        // Aqui você navega para a próxima tela do almoxarifado
        Alert.alert('Login', 'Requisição enviada com sucesso');
      } else {
        Alert.alert('Erro', 'Usuário ou senha inválidos');
      }
    } catch (e) {
      Alert.alert('Erro', 'Não foi possível conectar ao servidor');
    }
  }

  return (
    <KeyboardAvoidingView
      style={styles.corpo}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <StatusBar barStyle="light-content" />
      <ScrollView
        contentContainerStyle={styles.scroll}
        keyboardShouldPersistTaps="handled"
      >
        {/* static/logo2.PNG -> coloque o arquivo em ./assets/logo2.png */}
        <Image
          source={require('./assets/logo2.png')}
          style={styles.imagem}
          resizeMode="contain"
        />

        <View style={styles.bloco}>
          <Text style={styles.titulo}>Usuário</Text>
          <View style={styles.caixa}>
            <TextInput
              style={styles.input}
              placeholder="Digite seu usuário"
              placeholderTextColor="#B5C7D8"
              value={usuario}
              onChangeText={setUsuario}
              autoCapitalize="none"
              autoCorrect={false}
            />
          </View>

          <Text style={[styles.titulo, { marginTop: 20 }]}>Senha</Text>
          <View style={styles.caixa}>
            <TextInput
              style={styles.input}
              placeholder="Digite sua senha"
              placeholderTextColor="#B5C7D8"
              value={senha}
              onChangeText={setSenha}
              secureTextEntry={!mostrarSenha}
              autoCapitalize="none"
              autoCorrect={false}
            />
            <TouchableOpacity style={styles.olhinho} onPress={toggleSenha}>
              <Text>👁️</Text>
            </TouchableOpacity>
          </View>

          <TouchableOpacity style={styles.entrar} onPress={entrar}>
            <Text style={styles.entrarTexto}>Entrar</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const AZUL = '#005583';

const styles = StyleSheet.create({
  corpo: {
    flex: 1,
    backgroundColor: AZUL,
  },
  scroll: {
    flexGrow: 1,
    alignItems: 'center',
    paddingTop: 70,
    paddingHorizontal: 20,
    paddingBottom: 40,
  },
  imagem: {
    width: 260,
    height: 130,
    marginBottom: 40,
  },
  bloco: {
    width: '100%',
    maxWidth: 420,
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    paddingHorizontal: 24,
    paddingVertical: 32,
  },
  titulo: {
    color: AZUL,
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  caixa: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#EEF4FB',
    borderWidth: 2,
    borderColor: '#B8C7D6',
    borderRadius: 6,
    height: 50,
  },
  input: {
    flex: 1,
    height: '100%',
    paddingHorizontal: 8,
    fontSize: 17,
    color: '#1B2A38',
  },
  olhinho: {
    marginRight: 8,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderWidth: 1,
    borderColor: '#BBBBBB',
    backgroundColor: '#F2F2F2',
    borderRadius: 3,
  },
  entrar: {
    alignSelf: 'center',
    marginTop: 30,
    width: 200,
    height: 70,
    backgroundColor: AZUL,
    borderWidth: 2,
    borderColor: '#0B1A24',
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  entrarTexto: {
    color: '#FFFFFF',
    fontSize: 14,
  },
});