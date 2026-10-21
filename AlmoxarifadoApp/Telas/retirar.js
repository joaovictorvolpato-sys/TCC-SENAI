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

export default function Retirar({ navigation }) {
  const [operacao, setOperacao] = useState('Entrada');
  const [nomeItem, setNomeItem] = useState('');
  const [categoria, setCategoria] = useState('');
  const [funcao, setFuncao] = useState('');
  const [quantidade, setQuantidade] = useState('');

  // Equivale ao <form action="/retirar" method="POST">
  async function movimentar() {
    if (!nomeItem.trim() || !quantidade.trim()) {
      Alert.alert('Atenção', 'Preencha o nome do item e a quantidade');
      return;
    }

    const controle = new AbortController();
    const limite = setTimeout(() => controle.abort(), 5000);

    try {
      const corpo = new URLSearchParams({
        operacao: operacao,
        nomeItem: nomeItem,
        categoria: categoria,
        funcao: funcao,
        quantidade: quantidade,
      }).toString();

      const resposta = await fetch(API_URL + '/retirar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: corpo,
        signal: controle.signal,
      });
      clearTimeout(limite);

      if (resposta.ok) {
        Alert.alert('Sucesso', 'Movimentação registrada');
        setNomeItem('');
        setCategoria('');
        setFuncao('');
        setQuantidade('');
      } else {
        Alert.alert('Erro', 'Não foi possível registrar a movimentação');
      }
    } catch (e) {
      clearTimeout(limite);
      console.log('Erro:', e);
      Alert.alert('Erro', 'Não foi possível conectar ao servidor');
    }
  }

  return (
    <KeyboardAvoidingView
      style={styles.corpo}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      <StatusBar barStyle="light-content" backgroundColor={AZUL} />

      {/* <header id="cabecalho"> */}
      <View style={styles.cabecalho}>
        <Text style={styles.cabecalhoTitulo}>Retirar itens do estoque</Text>
        <Text style={styles.cabecalhoSub}>Controle de estoque</Text>
      </View>

      {/* <div id="formulario_retirar"> */}
      <ScrollView
        contentContainerStyle={styles.formulario}
        keyboardShouldPersistTaps="handled"
      >
        {/* <select name="operacao"> */}
        <View style={styles.seletor}>
          <TouchableOpacity
            style={[
              styles.opcao,
              operacao === 'Entrada' && styles.opcaoAtiva,
            ]}
            onPress={() => setOperacao('Entrada')}
          >
            <Text
              style={[
                styles.opcaoTexto,
                operacao === 'Entrada' && styles.opcaoTextoAtivo,
              ]}
            >
              Entrada
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[
              styles.opcao,
              operacao === 'Saida' && styles.opcaoAtiva,
            ]}
            onPress={() => setOperacao('Saida')}
          >
            <Text
              style={[
                styles.opcaoTexto,
                operacao === 'Saida' && styles.opcaoTextoAtivo,
              ]}
            >
              Saída
            </Text>
          </TouchableOpacity>
        </View>

        <Text style={styles.label}>Nome do Item</Text>
        <TextInput
          style={styles.input}
          value={nomeItem}
          onChangeText={setNomeItem}
        />

        <Text style={styles.label}>Categoria</Text>
        <TextInput
          style={styles.input}
          value={categoria}
          onChangeText={setCategoria}
        />

        <Text style={styles.label}>Função</Text>
        <TextInput
          style={styles.input}
          value={funcao}
          onChangeText={setFuncao}
        />

        <Text style={styles.label}>Quantidade</Text>
        <TextInput
          style={styles.input}
          value={quantidade}
          onChangeText={setQuantidade}
          keyboardType="numeric"
        />

        <TouchableOpacity style={styles.botao} onPress={movimentar}>
          <Text style={styles.botaoTexto}>Movimentar</Text>
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const AZUL = '#005583';

const styles = StyleSheet.create({
  corpo: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  cabecalho: {
    backgroundColor: AZUL,
    alignItems: 'center',
    paddingTop: 50,
    paddingBottom: 24,
    paddingHorizontal: 16,
  },
  cabecalhoTitulo: {
    color: '#FFFFFF',
    fontSize: 26,
    fontWeight: '500',
    textAlign: 'center',
  },
  cabecalhoSub: {
    color: '#FFFFFF',
    fontSize: 15,
    marginTop: 8,
  },
  formulario: {
    padding: 24,
    paddingTop: 40,
  },
  seletor: {
    flexDirection: 'row',
    alignSelf: 'flex-start',
    borderWidth: 2,
    borderColor: '#000000',
    borderRadius: 4,
    overflow: 'hidden',
    marginBottom: 12,
  },
  opcao: {
    paddingHorizontal: 14,
    paddingVertical: 6,
    backgroundColor: '#FFFFFF',
  },
  opcaoAtiva: {
    backgroundColor: AZUL,
  },
  opcaoTexto: {
    color: '#000000',
    fontSize: 16,
  },
  opcaoTextoAtivo: {
    color: '#FFFFFF',
    fontWeight: 'bold',
  },
  label: {
    color: '#1B2A38',
    fontSize: 16,
    marginBottom: 4,
  },
  input: {
    borderWidth: 1,
    borderColor: '#CED4DA',
    borderRadius: 6,
    height: 46,
    paddingHorizontal: 12,
    fontSize: 16,
    color: '#1B2A38',
    marginBottom: 14,
  },
  botao: {
    alignSelf: 'flex-start',
    backgroundColor: AZUL,
    paddingHorizontal: 16,
    paddingVertical: 10,
    borderRadius: 6,
    marginTop: 4,
  },
  botaoTexto: {
    color: '#FFFFFF',
    fontSize: 16,
  },
});