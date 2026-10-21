import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  StatusBar,
} from 'react-native';

import { API_URL } from '../config';

export default function Usuarios({ navigation }) {
  const [usuario, setUsuario] = useState('');
  const [senha, setSenha] = useState('');
  const [confirmarSenha, setConfirmarSenha] = useState('');
  const [mostrarSenha, setMostrarSenha] = useState(false);

  function limparCampos() {
    setUsuario('');
    setSenha('');
    setConfirmarSenha('');
  }

  // Equivale ao <form action="/cadastrar_usuario" method="POST">
  async function cadastrar() {
    if (!usuario.trim() || !senha) {
      Alert.alert('Atenção', 'Informe o usuário e a senha');
      return;
    }
    if (senha !== confirmarSenha) {
      Alert.alert('Atenção', 'As senhas não conferem');
      return;
    }

    const controle = new AbortController();
    const limite = setTimeout(() => controle.abort(), 5000);

    try {
      const corpo = new URLSearchParams({
        username: usuario.trim(),
        password: senha,
      }).toString();

      const resposta = await fetch(API_URL + '/cadastrar_usuario', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: corpo,
        signal: controle.signal,
      });
      clearTimeout(limite);
      console.log('Status:', resposta.status);

      if (resposta.ok) {
        Alert.alert('Sucesso', 'Usuário cadastrado com sucesso');
        limparCampos();
      } else {
        Alert.alert('Erro', 'Não foi possível cadastrar o usuário');
      }
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
        <View style={styles.cabecalho}>
          <Text style={styles.cabecalhoTitulo}>Cadastrar usuário</Text>
          <Text style={styles.cabecalhoSub}>Controle de estoque</Text>
        </View>

        <View style={styles.bloco}>
          <Text style={styles.titulo}>Usuário</Text>
          <View style={styles.caixa}>
            <TextInput
              style={styles.input}
              placeholder="Digite o usuário"
              placeholderTextColor="#B5C7D8"
              value={usuario}
              onChangeText={setUsuario}
              autoCapitalize="none"
              autoCorrect={false}
            />
          </View>

          <Text style={[styles.titulo, styles.espaco]}>Senha</Text>
          <View style={styles.caixa}>
            <TextInput
              style={styles.input}
              placeholder="Digite a senha"
              placeholderTextColor="#B5C7D8"
              value={senha}
              onChangeText={setSenha}
              secureTextEntry={!mostrarSenha}
              autoCapitalize="none"
              autoCorrect={false}
            />
            <TouchableOpacity
              style={styles.olhinho}
              onPress={() => setMostrarSenha(!mostrarSenha)}
            >
              <Text>👁️</Text>
            </TouchableOpacity>
          </View>

          <Text style={[styles.titulo, styles.espaco]}>Confirmar senha</Text>
          <View style={styles.caixa}>
            <TextInput
              style={styles.input}
              placeholder="Digite a senha novamente"
              placeholderTextColor="#B5C7D8"
              value={confirmarSenha}
              onChangeText={setConfirmarSenha}
              secureTextEntry={!mostrarSenha}
              autoCapitalize="none"
              autoCorrect={false}
            />
          </View>

          <TouchableOpacity style={styles.entrar} onPress={cadastrar}>
            <Text style={styles.entrarTexto}>Cadastrar</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.voltar}
            onPress={() => navigation.goBack()}
          >
            <Text style={styles.voltarTexto}>Voltar</Text>
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
    paddingTop: 60,
    paddingHorizontal: 20,
    paddingBottom: 40,
  },
  cabecalho: {
    alignItems: 'center',
    marginBottom: 30,
  },
  cabecalhoTitulo: {
    color: '#FFFFFF',
    fontSize: 28,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  cabecalhoSub: {
    color: '#FFFFFF',
    fontSize: 16,
    marginTop: 6,
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
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  espaco: {
    marginTop: 20,
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
  voltar: {
    alignSelf: 'center',
    marginTop: 16,
    padding: 8,
  },
  voltarTexto: {
    color: AZUL,
    fontSize: 15,
  },
});