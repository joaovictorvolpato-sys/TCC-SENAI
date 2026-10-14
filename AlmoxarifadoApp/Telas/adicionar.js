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
import * as ImagePicker from 'expo-image-picker';

import { API_URL } from '../config';

// Envia o FormData pelo XMLHttpRequest, que aceita { uri, name, type }
function enviarFormulario(dados) {
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', API_URL + '/cadastrar_item');
    xhr.timeout = 10000;
    xhr.onload = () =>
      resolve({ ok: xhr.status >= 200 && xhr.status < 400, status: xhr.status });
    xhr.onerror = () => reject(new Error('Falha de rede'));
    xhr.ontimeout = () => reject(new Error('Tempo esgotado'));
    xhr.send(dados);
  });
}

export default function AdicionarEstoque({ navigation }) {
  const [nomeItem, setNomeItem] = useState('');
  const [categoria, setCategoria] = useState('');
  const [funcao, setFuncao] = useState('');
  const [quantidade, setQuantidade] = useState('');
  const [valor, setValor] = useState('');
  const [foto, setFoto] = useState(null);

  // Equivale ao <input type="file" accept="image/*">
  async function escolherFoto() {
    const permissao = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permissao.granted) {
      Alert.alert('Permissão', 'Permita o acesso às fotos para escolher a imagem');
      return;
    }

    const resultado = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      quality: 0.7,
    });

    if (!resultado.canceled) {
      setFoto(resultado.assets[0]);
    }
  }

  function limparCampos() {
    setNomeItem('');
    setCategoria('');
    setFuncao('');
    setQuantidade('');
    setValor('');
    setFoto(null);
  }

  // Equivale ao <form action="/cadastrar_item" method="POST" enctype="multipart/form-data">
  async function cadastrar() {
    if (!nomeItem.trim()) {
      Alert.alert('Atenção', 'Informe o nome do item');
      return;
    }

    try {
      const dados = new FormData();
      dados.append('nome_item', nomeItem);
      dados.append('categoria', categoria);
      dados.append('funcao', funcao);
      dados.append('quantidade', quantidade);
      dados.append('valor', valor.replace(',', '.'));

      if (foto) {
        dados.append('foto', {
          uri: foto.uri,
          name: foto.fileName || 'foto.jpg',
          type: foto.mimeType || 'image/jpeg',
        });
      }

      const resposta = await enviarFormulario(dados);
      console.log('Status:', resposta.status);

      if (resposta.ok) {
        Alert.alert('Sucesso', 'Item cadastrado com sucesso');
        limparCampos();
      } else {
        Alert.alert('Erro', 'Não foi possível cadastrar o item');
      }
    } catch (e) {
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
        {/* Equivale ao <header id="cabecalho"> */}
        <View style={styles.cabecalho}>
          <Text style={styles.cabecalhoTitulo}>Adicionar itens ao estoque</Text>
          <Text style={styles.cabecalhoSub}>Controle de estoque</Text>
        </View>

        <View style={styles.bloco}>
          <Text style={styles.titulo}>Nome do Item</Text>
          <View style={styles.caixa}>
            <TextInput
              style={styles.input}
              placeholder="Digite o nome do item"
              placeholderTextColor="#B5C7D8"
              value={nomeItem}
              onChangeText={setNomeItem}
            />
          </View>

          <Text style={[styles.titulo, styles.espaco]}>Categoria</Text>
          <View style={styles.caixa}>
            <TextInput
              style={styles.input}
              placeholder="Digite a categoria"
              placeholderTextColor="#B5C7D8"
              value={categoria}
              onChangeText={setCategoria}
            />
          </View>

          <Text style={[styles.titulo, styles.espaco]}>Função</Text>
          <View style={styles.caixa}>
            <TextInput
              style={styles.input}
              placeholder="Digite a função"
              placeholderTextColor="#B5C7D8"
              value={funcao}
              onChangeText={setFuncao}
            />
          </View>

          <Text style={[styles.titulo, styles.espaco]}>Quantidade</Text>
          <View style={styles.caixa}>
            <TextInput
              style={styles.input}
              placeholder="Digite a quantidade"
              placeholderTextColor="#B5C7D8"
              value={quantidade}
              onChangeText={setQuantidade}
              keyboardType="numeric"
            />
          </View>

          <Text style={[styles.titulo, styles.espaco]}>Valor</Text>
          <View style={styles.caixa}>
            <TextInput
              style={styles.input}
              placeholder="Digite o valor"
              placeholderTextColor="#B5C7D8"
              value={valor}
              onChangeText={setValor}
              keyboardType="decimal-pad"
            />
          </View>

          <Text style={[styles.titulo, styles.espaco]}>Foto do seu Item</Text>
          <TouchableOpacity style={styles.botaoFoto} onPress={escolherFoto}>
            <Text style={styles.botaoFotoTexto}>
              {foto ? 'Trocar foto' : 'Escolher arquivo'}
            </Text>
          </TouchableOpacity>

          {foto && (
            <Image
              source={{ uri: foto.uri }}
              style={styles.preview}
              resizeMode="cover"
            />
          )}

          <TouchableOpacity style={styles.entrar} onPress={cadastrar}>
            <Text style={styles.entrarTexto}>Cadastrar</Text>
          </TouchableOpacity>

          <TouchableOpacity style={styles.voltar} onPress={() => navigation.goBack()}>
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
  botaoFoto: {
    alignSelf: 'flex-start',
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderWidth: 1,
    borderColor: '#BBBBBB',
    backgroundColor: '#F2F2F2',
    borderRadius: 4,
  },
  botaoFotoTexto: {
    color: '#1B2A38',
    fontSize: 15,
  },
  preview: {
    width: '100%',
    height: 180,
    borderRadius: 6,
    marginTop: 14,
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