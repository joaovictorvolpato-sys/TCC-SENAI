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

import { API_URL } from '../config';

// Funções que o Flask trata como administrador (FUNCOES_ADMIN no app.py)
const FUNCOES_ADMIN = ['administrador', 'admin'];

export default function Login({ navigation }) {
  const [usuario, setUsuario] = useState('');
  const [senha, setSenha] = useState('');
  const [mostrarSenha, setMostrarSenha] = useState(false);
  function toggleSenha() {
    setMostrarSenha(!mostrarSenha);
  }
  async function entrar() {
    if (!usuario.trim() || !senha) {
      Alert.alert('Atenção', 'Informe o usuário e a senha');
      return;
    }

    // Se o servidor não responder em 5 segundos, cancela e mostra o erro
    const controle = new AbortController();
    const limite = setTimeout(() => controle.abort(), 5000);

    try {
      const resposta = await fetch(API_URL + '/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: usuario.trim(),
          password: senha,
        }),
        signal: controle.signal,
      });
      clearTimeout(limite);
      console.log('Status:', resposta.status);

      if (!resposta.ok) {
        Alert.alert('Erro', 'Usuário ou senha inválidos');
        return;
      }

      const dados = await resposta.json(); // { usuario, funcao }
      console.log('Funcao recebida:', dados.funcao);

      const ehAdmin = FUNCOES_ADMIN.includes(
        String(dados.funcao).trim().toLowerCase()
      );

      // replace evita voltar para o login com o botão voltar
      navigation.replace(ehAdmin ? 'Inicial' : 'inicio.usuario');
    } catch (e) {
      clearTimeout(limite);
      console.log('Erro:', e.message);
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
        <Image
          source={require('../assets/logo2.png')}
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
  corpo: { flex: 1, backgroundColor: AZUL },
  scroll: {
    flexGrow: 1,
    alignItems: 'center',
    paddingTop: 70,
    paddingHorizontal: 20,
    paddingBottom: 40,
  },
  imagem: { width: 260, height: 130, marginBottom: 40 },
  bloco: {
    width: '100%',
    maxWidth: 420,
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    paddingHorizontal: 24,
    paddingVertical: 32,
  },
  titulo: { color: AZUL, fontSize: 24, fontWeight: 'bold', marginBottom: 8 },
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
  entrarTexto: { color: '#FFFFFF', fontSize: 14 },
});